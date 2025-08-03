import json
import re
import csv
import itertools

def generate_code_list(codebase):
    """
    Generates a list of code permutations based on a codebase string.
    - ';' defines ordered parts that separate independent permutation blocks.
    - '|' defines parts within a block that can be permuted.
    - '(x&y)' defines a bundled, ordered group treated as a single token within a block.
    """
    if not codebase:
        return []

    # Split the codebase by ';' to identify independent blocks
    sections = codebase.split(';')
    
    all_permutations_for_sections = []

    for section in sections:
        if not section:
            continue

        if '|' in section:
            # This is a permutation block
            # Extract individual elements or bundled elements
            elements_to_permute = []
            # Regex to find bundled groups (e.g., (x&y)) or individual codes
            # This regex needs to be careful about nested structures if they were allowed, but here only (x&y) is.
            # We split by '|' but need to handle potential '&' within bundles.
            
            # A more robust approach to split by '|' while respecting (x&y) bundles
            # We can use findall to get all codes and bundled codes
            # This regex captures either a non-parenthesis string (code) or a (non-greedy) parenthesis group.
            # Example: '03|04|(11&12)' -> ['03', '04', '(11&12)']
            parts_within_section = re.findall(r'\([^)]+\)|[^|]+', section)
            
            processed_parts = []
            for part in parts_within_section:
                if part.startswith('(') and part.endswith(')'):
                    # This is a bundled group, e.g., '(x&y)'
                    # Remove parentheses and replace '&' with ';'
                    processed_parts.append(part[1:-1].replace('&', ';'))
                else:
                    # This is a regular code
                    processed_parts.append(part)
            
            # Generate permutations for this block
            block_permutations = list(itertools.permutations(processed_parts))
            
            # Join permutations with ';' and store
            joined_block_perms = [';'.join(p) for p in block_permutations]
            all_permutations_for_sections.append(joined_block_perms)
        else:
            # This is a fixed part, treat as a single permutation
            all_permutations_for_sections.append([section])
            
    # Combine permutations from all sections using product (Cartesian product)
    # Example: [['A'], ['B1', 'B2'], ['C']] -> [('A', 'B1', 'C'), ('A', 'B2', 'C')]
    final_combinations = list(itertools.product(*all_permutations_for_sections))
    
    # Join the final combinations with ';' to form the codeList
    code_list = [';'.join(item) for item in final_combinations]
    
    return code_list

def update_and_add_rules(json_path, txt_path):
    """
    Updates 'codebase' in a JSON file based on a text file,
    and adds any rules from the text file that are missing in the JSON file.

    Args:
        json_path (str): The path to the JSON file.
        txt_path (str): The path to the text file containing rules.
    """
    try:
        # Step 1: Load existing JSON data
        with open(json_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)

        # Clean the list by removing invalid entries (e.g., empty dicts or no id)
        rules_map = data.get('rulesMap', [])
        original_count = len(rules_map)
        data['rulesMap'] = [rule for rule in rules_map if rule and 'id' in rule]
        cleaned_count = len(data['rulesMap'])
        if original_count != cleaned_count:
            print(f"Data Cleaning: Removed {original_count - cleaned_count} invalid rule entries from JSON data.")

        # Create a map of existing rules for efficient lookup
        existing_rules = {rule.get('id'): rule for rule in data.get('rulesMap', [])}
        
        updated_count = 0
        added_count = 0

        # Step 2: Read rules from the text file and process them
        rules_from_txt = {}
        with open(txt_path, 'r', encoding='utf-8') as txtfile:
            for line_idx, line in enumerate(txtfile):
                line = line.strip()
                if not line:
                    continue

                # Look for lines in format: （ID）codebase,description or (ID);codebase;;;description
                # Example: （1）01;3;02,某个项目的订单 or (1);01;02|03;;;某个项目的货单
                match = re.match(r'^（(\d+)）([^,]+),(.*)$', line)  # Po format
                if not match:
                    # Try VPO format: description;(ID);codebase;;;...
                    # Example: 查询项目的合同信息审核单;(1);01;04;03;02;;;;;;;;;;;;;;;;;;;;;;;
                    vpo_parts = line.split(';')
                    if len(vpo_parts) >= 3 and len(vpo_parts) > 1 and vpo_parts[1].startswith('(') and vpo_parts[1].endswith(')'):
                        # Extract ID from (ID)
                        id_part = vpo_parts[1][1:-1]  # Remove parentheses
                        if id_part.isdigit():
                            rule_id = int(id_part)
                            description = vpo_parts[0].strip()  # Description is first part
                            # Build codebase from meaningful parts (skip description and ID)
                            codebase_parts = []
                            for i in range(2, len(vpo_parts)):  # Skip description and ID
                                part = vpo_parts[i].strip()
                                if part:  # Only add non-empty parts
                                    codebase_parts.append(part)
                            codebase_part = ';'.join(codebase_parts)
                            # Create a match object-like structure
                            class VpoMatch:
                                def group(self, n):
                                    if n == 1: return str(rule_id)
                                    elif n == 2: return codebase_part
                                    elif n == 3: return description
                            match = VpoMatch()
                if not match:
                                         # Try Cargo format: (ID);code1;code2|code3;...;description
                     # Example: (1);01;02|03;;;某个项目的货单
                     cargo_parts = line.split(';')
                     if len(cargo_parts) >= 3 and cargo_parts[0].startswith('(') and cargo_parts[0].endswith(')'):
                         # Extract ID from (ID)
                         id_part = cargo_parts[0][1:-1]  # Remove parentheses
                         if id_part.isdigit():
                             rule_id = int(id_part)
                             # Find the description (last non-empty part)
                             description = cargo_parts[-1]
                             # Build codebase from meaningful parts (exclude empty and description)
                             codebase_parts = []
                             for i in range(1, len(cargo_parts) - 1):  # Skip ID and description
                                 part = cargo_parts[i].strip()
                                 if part:  # Only add non-empty parts
                                     codebase_parts.append(part)
                             codebase_part = ';'.join(codebase_parts)
                             # Create a match object-like structure
                             class CargoMatch:
                                 def group(self, n):
                                     if n == 1: return str(rule_id)
                                     elif n == 2: return codebase_part
                                     elif n == 3: return description
                             match = CargoMatch()
                if not match:
                    continue
                
                rule_id = int(match.group(1))
                codebase_part = match.group(2).strip()
                description = match.group(3).strip()
                
                # Process the codebase part
                # Split by semicolon and process each part
                parts = codebase_part.split(';')
                meaningful_parts = []
                
                for i, part in enumerate(parts):
                    part = part.strip()
                    if not part:
                        continue
                    
                    # Normalize single digit codes to two digits (e.g., "3" -> "03")
                    if part.isdigit() and len(part) == 1:
                        part = f"0{part}"
                    
                    meaningful_parts.append(part)
                
                codebase_from_txt = ';'.join(meaningful_parts) if len(meaningful_parts) > 1 else (meaningful_parts[0] if meaningful_parts else "")
                
                rules_from_txt[rule_id] = {
                    'codebase': codebase_from_txt,
                    'name': description if description else f"新规则 (ID: {rule_id})"
                }

        # Process rules from TXT: add new ones, update existing ones
        for rule_id, txt_rule_info in rules_from_txt.items():
            codebase_str = txt_rule_info['codebase']
            code_list = generate_code_list(codebase_str) # Use the enhanced function
            code_count = len(code_list[0].split(';')) if code_list else 0

            if rule_id in existing_rules:
                # Update existing rule
                existing_rule = existing_rules[rule_id]
                # Update if codebase, codeList, codecount, or name has changed
                if existing_rule.get('codebase') != codebase_str or \
                   existing_rule.get('codeList') != code_list or \
                   existing_rule.get('codecount') != code_count or \
                   existing_rule.get('name') != txt_rule_info['name']:
                    
                    # Print values before update for comparison
                    print(f"Updating rule for ID {rule_id}: codebase='{existing_rule.get('codebase')}' -> '{codebase_str}', "
                          f"codeList='{existing_rule.get('codeList')}' -> '{code_list}', "
                          f"codecount='{existing_rule.get('codecount')}' -> '{code_count}'.")

                    existing_rule['codebase'] = codebase_str
                    existing_rule['codeList'] = code_list
                    existing_rule['codecount'] = code_count
                    existing_rule['name'] = txt_rule_info['name']  # Also update name
                    updated_count += 1
                # else: print(f"Rule ID {rule_id} already up-to-date. (No codebase change, or codeList/codecount match)") # For debugging
            else:
                # Add new rule
                new_rule = {
                    'id': rule_id,
                    'name': txt_rule_info.get('name', f"新规则 (ID: {rule_id})"), # Use name from TXT if available
                    'codebase': codebase_str,
                    'codeList': code_list,
                    'codecount': code_count,
                    'rules': '', # Default empty
                    'prompt': '' # Default empty
                }
                data['rulesMap'].append(new_rule)
                added_count += 1
                print(f"Added new rule with ID {rule_id}: codebase='{codebase_str}', codeList='{code_list}', codecount='{code_count}'.")

        # Step 3: Clean up rules that exist in JSON but not in TXT
        removed_count = 0
        rules_to_keep = []
        for rule in data['rulesMap']:
            rule_id = rule.get('id')
            if rule_id in rules_from_txt:
                rules_to_keep.append(rule)
            else:
                print(f"Removing rule ID {rule_id} (exists in JSON but not in TXT file)")
                removed_count += 1
        
        if removed_count > 0:
            data['rulesMap'] = rules_to_keep
        
        # Step 4: Write the updated data back to the JSON file if changes were made
        if updated_count > 0 or added_count > 0 or cleaned_count > 0 or removed_count > 0: # Also write if only cleaned or removed
            # Sort the rulesMap by ID before saving, safely handling items without an 'id'
            data['rulesMap'] = sorted(data['rulesMap'], key=lambda x: x.get('id', 0))
            
            with open(json_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            print(f"Successfully wrote changes to {json_path}.")
        else:
            print("No rule updates or additions were necessary.")

        print(f"\nSummary:\n- Rules updated (codeList regenerated): {updated_count}\n- New rules added: {added_count}\n- Rules removed (not in TXT): {removed_count}\n- Total rules in {json_path}: {len(data['rulesMap'])}")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {json_path} - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    JSON_FILE_PATH = 'src/entity/relationship/searchCargoRules.json'
    TXT_FILE_PATH = 'rules/cost/searchCargo'
    update_and_add_rules(JSON_FILE_PATH, TXT_FILE_PATH)
