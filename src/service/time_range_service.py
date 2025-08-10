import os
import re
import json
import random
import datetime
import calendar
from typing import Dict, Any, List, Tuple, Optional


# TimeRange policy and helpers (no external deps; Asia/Shanghai has no DST)
class TimeRangePolicy:
    def __init__(
        self,
        tz: str = "Asia/Shanghai",
        include_today_for_recent: bool = True,
        exclude_today_for_prev_next: bool = True,
        forbid_future_end: bool = True,
        max_span_years: int = 10,
        week_start: str = "Mon",
    ):
        self.tz = tz
        self.include_today_for_recent = include_today_for_recent
        self.exclude_today_for_prev_next = exclude_today_for_prev_next
        self.forbid_future_end = forbid_future_end
        self.max_span_years = max_span_years
        self.week_start = week_start


def _fmt(dt: datetime.datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _parse_reference_time(reference_time: Optional[str]) -> datetime.datetime:
    if reference_time:
        return datetime.datetime.strptime(reference_time, "%Y-%m-%d %H:%M:%S")
    # default to now (local). Treat as Asia/Shanghai logically; no DST handling needed per spec
    return datetime.datetime.now()


def _start_of_day(d: datetime.date) -> datetime.datetime:
    return datetime.datetime(d.year, d.month, d.day, 0, 0, 0)


def _end_of_day(d: datetime.date) -> datetime.datetime:
    return datetime.datetime(d.year, d.month, d.day, 23, 59, 59)


def _clamp_end(end_dt: datetime.datetime, now_dt: datetime.datetime, forbid_future: bool) -> datetime.datetime:
    if forbid_future and end_dt > now_dt:
        return now_dt
    return end_dt


def _compute_this_week(ref: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
    # ISO: Monday=0..Sunday=6
    weekday = ref.weekday()
    monday = (ref - datetime.timedelta(days=weekday)).date()
    start_dt = _start_of_day(monday)
    sunday = monday + datetime.timedelta(days=6)
    end_dt = _end_of_day(sunday)
    return start_dt, end_dt


def _compute_last_month(ref: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
    year = ref.year
    month = ref.month
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    start_dt = datetime.datetime(prev_year, prev_month, 1, 0, 0, 0)
    last_day = calendar.monthrange(prev_year, prev_month)[1]
    end_dt = datetime.datetime(prev_year, prev_month, last_day, 23, 59, 59)
    return start_dt, end_dt



def _compute_this_month(ref: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
    start_dt = datetime.datetime(ref.year, ref.month, 1, 0, 0, 0)
    last_day = calendar.monthrange(ref.year, ref.month)[1]
    end_dt = datetime.datetime(ref.year, ref.month, last_day, 23, 59, 59)
    return start_dt, end_dt


def _compute_next_month(ref: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
    year, month = ref.year, ref.month
    if month == 12:
        y2, m2 = year + 1, 1
    else:
        y2, m2 = year, month + 1
    start_dt = datetime.datetime(y2, m2, 1, 0, 0, 0)
    last_day = calendar.monthrange(y2, m2)[1]
    end_dt = datetime.datetime(y2, m2, last_day, 23, 59, 59)
    return start_dt, end_dt


def _compute_this_year(ref: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
    start_dt = datetime.datetime(ref.year, 1, 1, 0, 0, 0)
    end_dt = datetime.datetime(ref.year, 12, 31, 23, 59, 59)
    return start_dt, end_dt


def _quarter_of_month(m: int) -> int:
    if 1 <= m <= 3:
        return 1
    if 4 <= m <= 6:
        return 2
    if 7 <= m <= 9:
        return 3
    return 4


def _compute_quarter_by_index(year: int, q: int) -> Tuple[datetime.datetime, datetime.datetime]:
    if q == 1:
        start_month, end_month = 1, 3
    elif q == 2:
        start_month, end_month = 4, 6
    elif q == 3:
        start_month, end_month = 7, 9
    else:
        start_month, end_month = 10, 12
    start_dt = datetime.datetime(year, start_month, 1, 0, 0, 0)
    last_day = calendar.monthrange(year, end_month)[1]
    end_dt = datetime.datetime(year, end_month, last_day, 23, 59, 59)
    return start_dt, end_dt


def _compute_this_quarter(ref: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
    q = _quarter_of_month(ref.month)
    return _compute_quarter_by_index(ref.year, q)


def _compute_last_quarter(ref: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
    q = _quarter_of_month(ref.month)
    if q == 1:
        return _compute_quarter_by_index(ref.year - 1, 4)
    return _compute_quarter_by_index(ref.year, q - 1)


def _compute_next_week(ref: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
    # start of current week (Mon)
    weekday = ref.weekday()
    monday = (ref - datetime.timedelta(days=weekday)).date()
    next_monday = monday + datetime.timedelta(days=7)
    start_dt = _start_of_day(next_monday)
    next_sunday = next_monday + datetime.timedelta(days=6)
    end_dt = _end_of_day(next_sunday)
    return start_dt, end_dt


def _compute_prev_n_days_exclude_today(ref: datetime.datetime, n: int) -> Tuple[datetime.datetime, datetime.datetime]:
    today = ref.date()
    start_date = today - datetime.timedelta(days=n)
    end_date = today - datetime.timedelta(days=1)
    return _start_of_day(start_date), _end_of_day(end_date)


def _compute_next_n_days_exclude_today(ref: datetime.datetime, n: int) -> Tuple[datetime.datetime, datetime.datetime]:
    today = ref.date()
    start_date = today + datetime.timedelta(days=1)
    end_date = today + datetime.timedelta(days=n)
    return _start_of_day(start_date), _end_of_day(end_date)


def _adjust_if_negative_after_clamp(start_dt: datetime.datetime, end_dt: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
    # 若截断后 end < start，则将 start 调整为 end 所在日的 00:00:00，保证非负区间
    if end_dt < start_dt:
        start_dt = _start_of_day(end_dt.date())
    return start_dt, end_dt


def _sample_reference_time_string() -> str:
    """随机生成参考时间字符串，覆盖月初/月末等边界概率更高。"""
    now = datetime.datetime.now()
    start_year = max(2018, now.year - 5)
    year = random.randint(start_year, now.year)
    month = random.randint(1, 12)
    # 保证合法天
    last_day = calendar.monthrange(year, month)[1]
    # 提高选中边界日概率
    day_choices = [1, 2, last_day - 1, last_day] + [random.randint(1, last_day) for _ in range(6)]
    day = random.choice(day_choices)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    try:
        dt = datetime.datetime(year, month, day, hour, minute, second)
    except ValueError:
        # 兜底非法日期
        dt = datetime.datetime(year, month, min(day, last_day), hour, minute, second)
    return _fmt(dt)


def _compute_past_n_days_include_today(ref: datetime.datetime, n: int) -> Tuple[datetime.datetime, datetime.datetime]:
    today = ref.date()
    # include today => [today-(n-1) .. today]
    start_date = today - datetime.timedelta(days=max(n - 1, 0))
    start_dt = _start_of_day(start_date)
    end_dt = _end_of_day(today)
    return start_dt, end_dt


def _compute_labor_day_plus_n(ref: datetime.datetime, n: int) -> Tuple[datetime.datetime, datetime.datetime]:
    # Labor Day fixed 5/1 in Gregorian calendar, same year as reference
    target_date = datetime.date(ref.year, 5, 1) + datetime.timedelta(days=n)
    start_dt = _start_of_day(target_date)
    end_dt = _end_of_day(target_date)
    return start_dt, end_dt


def _ensure_span_limit(start_dt: datetime.datetime, end_dt: datetime.datetime, max_years: int) -> None:
    if max_years is None:
        return
    # rough check: difference in days > max_years * 366
    if (end_dt - start_dt).days > max_years * 366:
        raise ValueError(f"时间跨度超过上限 {max_years} 年：{start_dt}..{end_dt}")


def parse_phrase_to_range(
    phrase: str,
    reference_time: Optional[str] = None,
    policy: Optional[TimeRangePolicy] = None,
) -> Dict[str, Any]:
    """
    Parse a time phrase into standardized interval per 规范_v1.
    Returns: { startTime, endTime, timeRange }
    """
    pol = policy or TimeRangePolicy()
    ref = _parse_reference_time(reference_time)
    now_dt = datetime.datetime.now()

    p = phrase.strip()
    start_dt: datetime.datetime
    end_dt: datetime.datetime

    # Normalize punctuations (remove optional parentheses suffix like （含今天）)
    p_clean = re.sub(r"（.*?）|\(.*?\)", "", p)

    # 本周
    if p_clean in ("本周", "这周", "本星期"):
        start_dt, end_dt = _compute_this_week(ref)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
    # 下周
    elif p_clean == "下周":
        start_dt, end_dt = _compute_next_week(ref)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
        start_dt, end_dt = _adjust_if_negative_after_clamp(start_dt, end_dt)
    # 本月
    elif p_clean in ("本月", "这个月"):
        start_dt, end_dt = _compute_this_month(ref)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
    # 上个月/上月
    elif p_clean in ("上个月", "上月"):
        start_dt, end_dt = _compute_last_month(ref)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
    # 下个月
    elif p_clean == "下个月":
        start_dt, end_dt = _compute_next_month(ref)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
        start_dt, end_dt = _adjust_if_negative_after_clamp(start_dt, end_dt)
    # 今年
    elif p_clean in ("今年",):
        start_dt, end_dt = _compute_this_year(ref)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
    # 本季度
    elif p_clean in ("本季度", "这个季度"):
        start_dt, end_dt = _compute_this_quarter(ref)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
    # 上季度
    elif p_clean in ("上季度",):
        start_dt, end_dt = _compute_last_quarter(ref)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
    # Q1/Q2/Q3/Q4
    elif m := re.match(r"^Q([1-4])$", p_clean, re.IGNORECASE):
        q = int(m.group(1))
        start_dt, end_dt = _compute_quarter_by_index(ref.year, q)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
    # 过去N天 / 最近N天（默认含今天）
    elif m := re.match(r"^(过去|最近)(\d+)天$", p_clean):
        n = int(m.group(2))
        start_dt, end_dt = _compute_past_n_days_include_today(ref, n)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
    # 前N天（不含今天）
    elif m := re.match(r"^前(\d+)天$", p_clean):
        n = int(m.group(1))
        start_dt, end_dt = _compute_prev_n_days_exclude_today(ref, n)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
    # 后N天（不含今天）
    elif m := re.match(r"^后(\d+)天$", p_clean):
        n = int(m.group(1))
        start_dt, end_dt = _compute_next_n_days_exclude_today(ref, n)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
        start_dt, end_dt = _adjust_if_negative_after_clamp(start_dt, end_dt)
    # 劳动节后N天（单点日区间）
    elif m := re.match(r"^劳动节后(\d+)天$", p_clean):
        n = int(m.group(1))
        start_dt, end_dt = _compute_labor_day_plus_n(ref, n)
        end_dt = _clamp_end(end_dt, now_dt, pol.forbid_future_end)
        if end_dt < start_dt:
            start_dt = _start_of_day(end_dt.date())
    else:
        raise ValueError(f"暂不支持的时间短语：{phrase}")

    # 全局调整：若未来截断导致 end < start，回退 start 至 end 当日 00:00:00，确保非负区间
    start_dt, end_dt = _adjust_if_negative_after_clamp(start_dt, end_dt)

    _ensure_span_limit(start_dt, end_dt, pol.max_span_years)

    time_range_sec = int((end_dt - start_dt).total_seconds())
    label = {
        "startTime": _fmt(start_dt),
        "endTime": _fmt(end_dt),
        "timeRange": time_range_sec,
    }
    return label


def build_sample(
    phrase: str,
    reference_time: Optional[str],
    policy: Optional[TimeRangePolicy],
    user_mode: str = "with_reference",
) -> Dict[str, Any]:
    label = parse_phrase_to_range(phrase, reference_time, policy)
    ref_time_out = reference_time or _fmt(_parse_reference_time(None))

    if user_mode == "with_reference":
        user_content = f"当前时间：{ref_time_out}；请解析：{phrase}"
    else:
        user_content = phrase

    assistant_content = json.dumps(
        {
            "startTime": label["startTime"],
            "endTime": label["endTime"],
            "timeRange": label["timeRange"],
        },
        ensure_ascii=False,
    )

    return {
        "reference_time": ref_time_out,
        "query": phrase,
        "label": label,
        "meta": {
            "tz": (policy.tz if policy else "Asia/Shanghai"),
            "weekStart": (policy.week_start if policy else "Mon"),
            "policy": {
                "includeTodayForRecent": (policy.include_today_for_recent if policy else True),
                "excludeTodayForPrevNext": (policy.exclude_today_for_prev_next if policy else True),
            },
            "generator": {
                "version": "1.0.0",
                "ruleId": "timeRange.v1",
            },
        },
        "messages": [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content},
        ],
    }


def generate_time_range_qwen_data(
    total_samples: int = 100,
    output_dir: str = os.path.join("outputs", "data", "qwen"),
    policy: Optional[TimeRangePolicy] = None,
    user_mode: str = "with_reference",
    enhancement_mode: str = "balanced",
) -> str:
    """
    Generate Qwen JSONL for time range phrases per 规范_v1.
    Returns: path to the JSONL file.
    """
    pol = policy or TimeRangePolicy()

    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = os.path.join(output_dir, f"timeRange_{total_samples}_{ts}.jsonl")


    # 根据增强模式选择不同的模板池
    if enhancement_mode == "disambiguation":
        # 专项增强：重点覆盖易混淆的时间表达对比
        phrase_pool = [
            # 含今天 vs 不含今天的对比组
            "过去{n}天", "最近{n}天",  # 含今天
            "前{n}天", "后{n}天",      # 不含今天
            # 边界敏感的固定表达
            "本周", "下周", "本月", "上个月", "下个月",
            "本季度", "上季度", "Q1", "Q2", "Q3", "Q4",
            # 节日偏移（单点测试）
            "劳动节后{n}天",
        ]
        # 增加数值候选，覆盖更多N值
        numeric_candidates = [1, 2, 3, 5, 7, 10, 14, 15, 20, 30, 45, 60, 90, 120]
    else:
        # 平衡模式：原有模板池
        phrase_pool = [
            "本周", "下周", "本月", "上个月", "下个月", "今年",
            "本季度", "上季度", "Q1", "Q2", "Q3", "Q4",
            "过去{n}天", "最近{n}天", "前{n}天", "后{n}天", "劳动节后{n}天",
        ]
        numeric_candidates = [3, 5, 7, 15, 30, 60, 90]


    written = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for _ in range(total_samples):
            tpl = random.choice(phrase_pool)
            if "{n}" in tpl:
                n = random.choice(numeric_candidates)
                phrase = tpl.format(n=n)
            else:
                phrase = tpl

            ref_time_str = _sample_reference_time_string()
            sample = build_sample(phrase, ref_time_str, pol, user_mode=user_mode)
            # Write Qwen message object only (messages array), consistent with qwen_service style
            qwen_obj = {"messages": sample["messages"]}
            f.write(json.dumps(qwen_obj, ensure_ascii=False) + "\n")
            written += 1

    return output_path





def generate_enhancement_dataset_for_disambiguation(
    total_samples: int = 8000,
    output_dir: str = os.path.join("outputs", "data", "qwen"),
    policy: Optional[TimeRangePolicy] = None,
) -> str:
    """
    生成专项增强数据集，重点解决时间表达的语义混淆问题。

    重点覆盖：
    1. "过去N天/最近N天"（含今天） vs "前N天/后N天"（不含今天）
    2. 边界日期：月底、季度末、闰年2月
    3. 同义变体与口语表达
    4. 对比样例：相同参考时间下的不同表达
    """
    pol = policy or TimeRangePolicy()
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = os.path.join(output_dir, f"timeRange_enhancement_{total_samples}_{ts}.jsonl")

    # 专项模板：重点覆盖易混淆表达
    confusion_pairs = [
        # 含今天 vs 不含今天的核心对比
        ("过去{n}天", "前{n}天"),
        ("最近{n}天", "前{n}天"),
        ("过去{n}天", "后{n}天"),
        ("最近{n}天", "后{n}天"),
    ]

    # 边界敏感的固定表达
    boundary_phrases = [
        "本周", "下周", "本月", "上个月", "下个月",
        "本季度", "上季度", "Q1", "Q2", "Q3", "Q4", "今年"
    ]

    # 数值范围：覆盖短期、中期、长期
    n_values = [1, 2, 3, 5, 7, 10, 14, 15, 20, 30, 45, 60, 90]

    # 边界参考时间：月初、月末、季度末、闰年等
    def generate_boundary_reference_times(count: int) -> List[str]:
        times = []
        for _ in range(count):
            year = random.randint(2020, 2025)
            # 提高边界概率
            if random.random() < 0.4:  # 40% 边界日
                month = random.randint(1, 12)
                if random.random() < 0.5:  # 月初
                    day = random.choice([1, 2])
                else:  # 月末
                    last_day = calendar.monthrange(year, month)[1]
                    day = random.choice([last_day - 1, last_day])
            else:  # 60% 普通日
                month = random.randint(1, 12)
                last_day = calendar.monthrange(year, month)[1]
                day = random.randint(1, last_day)

            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            dt = datetime.datetime(year, month, day, hour, minute, second)
            times.append(_fmt(dt))
        return times

    written = 0
    with open(output_path, "w", encoding="utf-8") as f:
        # 1. 对比样例：相同参考时间，不同表达
        contrast_samples = total_samples // 3
        for _ in range(contrast_samples):
            ref_time = random.choice(generate_boundary_reference_times(10))
            pair = random.choice(confusion_pairs)
            n = random.choice(n_values)

            # 生成对比的两个表达
            phrase1 = pair[0].format(n=n)
            phrase2 = pair[1].format(n=n)

            for phrase in [phrase1, phrase2]:
                try:
                    sample = build_sample(phrase, ref_time, pol, user_mode="with_reference")
                    qwen_obj = {"messages": sample["messages"]}
                    f.write(json.dumps(qwen_obj, ensure_ascii=False) + "\n")
                    written += 1
                except ValueError:
                    continue  # 跳过不支持的表达

        # 2. 边界固定表达
        boundary_samples = total_samples // 3
        boundary_ref_times = generate_boundary_reference_times(boundary_samples)
        for i in range(boundary_samples):
            phrase = random.choice(boundary_phrases)
            ref_time = boundary_ref_times[i % len(boundary_ref_times)]

            try:
                sample = build_sample(phrase, ref_time, pol, user_mode="with_reference")
                qwen_obj = {"messages": sample["messages"]}
                f.write(json.dumps(qwen_obj, ensure_ascii=False) + "\n")
                written += 1
            except ValueError:
                continue

        # 3. 随机混合（补足剩余样本）
        remaining = total_samples - written
        all_templates = [p.format(n="{n}") if "{n}" in p else p
                        for pair in confusion_pairs for p in pair] + boundary_phrases

        for _ in range(remaining):
            template = random.choice(all_templates)
            if "{n}" in template:
                n = random.choice(n_values)
                phrase = template.format(n=n)
            else:
                phrase = template

            ref_time = _sample_reference_time_string()
            try:
                sample = build_sample(phrase, ref_time, pol, user_mode="with_reference")
                qwen_obj = {"messages": sample["messages"]}
                f.write(json.dumps(qwen_obj, ensure_ascii=False) + "\n")
                written += 1
            except ValueError:
                continue

    return output_path


def validate_label(label: Dict[str, Any]) -> List[str]:
    errs: List[str] = []
    try:
        st = datetime.datetime.strptime(label["startTime"], "%Y-%m-%d %H:%M:%S")
        et = datetime.datetime.strptime(label["endTime"], "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return [f"时间格式错误: {e}"]

    if et < st:
        errs.append("endTime < startTime")

    expected = int((et - st).total_seconds())
    if expected != int(label.get("timeRange", -1)):
        errs.append(f"timeRange不匹配: 期望{expected}, 实际{label.get('timeRange')}")

    return errs


if __name__ == "__main__":
    # quick demo run: generate 100 samples with reference time in user message
    path = generate_time_range_qwen_data(total_samples=100, user_mode="with_reference")
    print(f"生成完成: {path}")

