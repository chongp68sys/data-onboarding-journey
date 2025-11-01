import pandas as pd
import re
from typing import Dict, List, Any
from difflib import SequenceMatcher
import os

class DataMappingTools:
    """Tools for data mapping, transformation, and schema operations"""
    
    def __init__(self, working_directory: str = "tmp"):
        self.working_directory = working_directory
        os.makedirs(working_directory, exist_ok=True)
    
    def suggest_column_mapping(self, source_columns: str, target_schema: str, similarity_threshold: float = 0.6) -> str:
        """Suggest column mappings based on similarity analysis
        
        Args:
            source_columns: Comma-separated list of source column names
            target_schema: Comma-separated list of target column names
            similarity_threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            JSON string with mapping suggestions
        """
        try:
            # Parse input strings to lists
            source_cols = [col.strip() for col in source_columns.split(',')]
            target_cols = [col.strip() for col in target_schema.split(',')]
            
            suggestions = {}
            mapping_confidence = {}
            
            for source_col in source_cols:
                best_match = None
                best_score = 0
                
                for target_col in target_cols:
                    # Calculate different similarity scores
                    exact_score = self._calculate_exact_similarity(source_col, target_col)
                    semantic_score = self._calculate_semantic_similarity(source_col, target_col)
                    fuzzy_score = self._calculate_fuzzy_similarity(source_col, target_col)
                    
                    # Weighted average
                    avg_score = (exact_score * 0.4 + semantic_score * 0.4 + fuzzy_score * 0.2)
                    
                    if avg_score > best_score and avg_score >= similarity_threshold:
                        best_score = avg_score
                        best_match = target_col
                
                if best_match:
                    suggestions[source_col] = best_match
                    mapping_confidence[source_col] = round(best_score, 3)
            
            result = {
                "success": True,
                "mapping_suggestions": suggestions,
                "confidence_scores": mapping_confidence,
                "threshold_used": similarity_threshold,
                "unmapped_source_columns": [col for col in source_cols if col not in suggestions],
                "unused_target_columns": [col for col in target_cols if col not in suggestions.values()],
                "total_source_columns": len(source_cols),
                "successful_mappings": len(suggestions)
            }
            
            return str(result)
            
        except Exception as e:
            return f"Error suggesting column mapping: {str(e)}"
    
    def clean_column_names(self, column_names: str, convention: str = "snake_case", remove_special_chars: bool = True) -> str:
        """Clean and standardize column names
        
        Args:
            column_names: Comma-separated list of column names to clean
            convention: Naming convention (snake_case, camelCase, PascalCase, lowercase)
            remove_special_chars: Whether to remove special characters
            
        Returns:
            JSON string with cleaned column names and mapping
        """
        try:
            # Parse input
            columns = [col.strip() for col in column_names.split(',')]
            
            cleaned_mapping = {}
            
            for col in columns:
                cleaned_name = col
                
                # Remove or replace special characters
                if remove_special_chars:
                    cleaned_name = re.sub(r'[^a-zA-Z0-9_\s]', '', cleaned_name)
                
                # Apply naming convention
                if convention == "snake_case":
                    cleaned_name = self._to_snake_case(cleaned_name)
                elif convention == "camelCase":
                    cleaned_name = self._to_camel_case(cleaned_name)
                elif convention == "PascalCase":
                    cleaned_name = self._to_pascal_case(cleaned_name)
                elif convention == "lowercase":
                    cleaned_name = cleaned_name.lower().replace(" ", "_")
                
                # Ensure name is not empty
                if not cleaned_name:
                    cleaned_name = f"column_{columns.index(col)}"
                
                cleaned_mapping[col] = cleaned_name
            
            result = {
                "success": True,
                "cleaning_convention": convention,
                "remove_special_chars": remove_special_chars,
                "original_columns": columns,
                "cleaned_columns": list(cleaned_mapping.values()),
                "column_mapping": cleaned_mapping,
                "duplicates_found": len(columns) != len(set(cleaned_mapping.values()))
            }
            
            return str(result)
            
        except Exception as e:
            return f"Error cleaning column names: {str(e)}"
    
    def validate_column_mapping(self, mapping_json: str, source_columns: str) -> str:
        """Validate a proposed column mapping
        
        Args:
            mapping_json: JSON string of proposed mapping (e.g., '{"old_col": "new_col"}')
            source_columns: Comma-separated list of available source columns
            
        Returns:
            JSON string with validation results
        """
        try:
            import json
            
            # Parse inputs
            try:
                mapping = json.loads(mapping_json)
            except:
                # Try parsing as simple dict string
                mapping = eval(mapping_json)
            
            source_cols = [col.strip() for col in source_columns.split(',')]
            
            validation_results = {
                "success": True,
                "valid_mappings": {},
                "invalid_mappings": {},
                "missing_source_columns": [],
                "duplicate_targets": {},
                "mapping_coverage": 0
            }
            
            # Check each mapping
            target_counts = {}
            
            for source, target in mapping.items():
                if source not in source_cols:
                    validation_results["invalid_mappings"][source] = f"Source column '{source}' not found"
                    validation_results["missing_source_columns"].append(source)
                else:
                    validation_results["valid_mappings"][source] = target
                    
                    # Track target duplicates
                    if target in target_counts:
                        target_counts[target] += 1
                    else:
                        target_counts[target] = 1
            
            # Identify duplicate targets
            validation_results["duplicate_targets"] = {
                target: count for target, count in target_counts.items() if count > 1
            }
            
            # Calculate coverage
            valid_source_count = len(validation_results["valid_mappings"])
            validation_results["mapping_coverage"] = round((valid_source_count / len(source_cols)) * 100, 2)
            
            # Overall success
            validation_results["success"] = (
                len(validation_results["invalid_mappings"]) == 0 and
                len(validation_results["duplicate_targets"]) == 0
            )
            
            return str(validation_results)
            
        except Exception as e:
            return f"Error validating column mapping: {str(e)}"
    
    def generate_mapping_template(self, source_columns: str, target_schema: str = None) -> str:
        """Generate a mapping template for manual completion
        
        Args:
            source_columns: Comma-separated list of source column names
            target_schema: Optional comma-separated list of target column names
            
        Returns:
            JSON string with mapping template
        """
        try:
            source_cols = [col.strip() for col in source_columns.split(',')]
            target_cols = []
            
            if target_schema:
                target_cols = [col.strip() for col in target_schema.split(',')]
            
            # Generate template
            mapping_template = {}
            suggestions = {}
            
            for source_col in source_cols:
                # Start with identity mapping
                mapping_template[source_col] = ""
                
                # Add suggestions if target schema provided
                if target_cols:
                    best_match = self._find_best_match(source_col, target_cols)
                    if best_match:
                        suggestions[source_col] = best_match
            
            result = {
                "success": True,
                "source_columns": source_cols,
                "target_schema": target_cols,
                "mapping_template": mapping_template,
                "auto_suggestions": suggestions,
                "instructions": [
                    "Fill in the mapping_template with your desired target column names",
                    "Use the auto_suggestions as a starting point",
                    "Ensure no duplicate target names",
                    "Leave blank to exclude a column from the output"
                ]
            }
            
            return str(result)
            
        except Exception as e:
            return f"Error generating mapping template: {str(e)}"
    
    def apply_data_transformations(self, transformation_rules: str) -> str:
        """Generate code for applying data transformations
        
        Args:
            transformation_rules: JSON string describing transformations
            
        Returns:
            Python code string for applying transformations
        """
        try:
            import json
            
            try:
                rules = json.loads(transformation_rules)
            except:
                rules = eval(transformation_rules)
            
            code_lines = [
                "# Generated data transformation code",
                "import pandas as pd",
                "import numpy as np",
                "from datetime import datetime",
                "",
                "def apply_transformations(df):",
                "    \"\"\"Apply the specified data transformations\"\"\"",
                "    df_transformed = df.copy()",
                ""
            ]
            
            for column, transforms in rules.items():
                if isinstance(transforms, dict):
                    for transform_type, params in transforms.items():
                        if transform_type == "rename":
                            code_lines.append(f"    df_transformed = df_transformed.rename(columns={{'{column}': '{params}'}})")
                        elif transform_type == "type_convert":
                            if params == "datetime":
                                code_lines.append(f"    df_transformed['{column}'] = pd.to_datetime(df_transformed['{column}'], errors='coerce')")
                            elif params == "numeric":
                                code_lines.append(f"    df_transformed['{column}'] = pd.to_numeric(df_transformed['{column}'], errors='coerce')")
                            else:
                                code_lines.append(f"    df_transformed['{column}'] = df_transformed['{column}'].astype('{params}')")
                        elif transform_type == "fill_na":
                            code_lines.append(f"    df_transformed['{column}'] = df_transformed['{column}'].fillna({repr(params)})")
                        elif transform_type == "strip_whitespace":
                            code_lines.append(f"    df_transformed['{column}'] = df_transformed['{column}'].astype(str).str.strip()")
                        elif transform_type == "uppercase":
                            code_lines.append(f"    df_transformed['{column}'] = df_transformed['{column}'].astype(str).str.upper()")
                        elif transform_type == "lowercase":
                            code_lines.append(f"    df_transformed['{column}'] = df_transformed['{column}'].astype(str).str.lower()")
            
            code_lines.extend([
                "",
                "    return df_transformed",
                "",
                "# Usage: transformed_df = apply_transformations(your_dataframe)"
            ])
            
            result = {
                "success": True,
                "transformation_code": "\n".join(code_lines),
                "rules_applied": len(rules),
                "instructions": [
                    "Copy the transformation_code to apply these changes",
                    "Test on a sample first before applying to full dataset",
                    "Review the generated code before execution"
                ]
            }
            
            return str(result)
            
        except Exception as e:
            return f"Error generating transformation code: {str(e)}"
    
    def _calculate_exact_similarity(self, str1: str, str2: str) -> float:
        """Calculate exact string similarity using SequenceMatcher"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _calculate_semantic_similarity(self, str1: str, str2: str) -> float:
        """Calculate semantic similarity based on common words"""
        words1 = set(re.findall(r'\w+', str1.lower()))
        words2 = set(re.findall(r'\w+', str2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_fuzzy_similarity(self, str1: str, str2: str) -> float:
        """Calculate fuzzy similarity with partial matching"""
        clean1 = re.sub(r'[^a-zA-Z0-9]', '', str1.lower())
        clean2 = re.sub(r'[^a-zA-Z0-9]', '', str2.lower())
        
        if clean1 in clean2 or clean2 in clean1:
            return 0.8
        
        return self._calculate_exact_similarity(clean1, clean2)
    
    def _find_best_match(self, source: str, targets: List[str]) -> str:
        """Find the best matching target for a source column"""
        best_match = None
        best_score = 0
        
        for target in targets:
            score = (
                self._calculate_exact_similarity(source, target) * 0.5 +
                self._calculate_semantic_similarity(source, target) * 0.5
            )
            if score > best_score:
                best_score = score
                best_match = target
        
        return best_match if best_score > 0.5 else None
    
    def _to_snake_case(self, name: str) -> str:
        """Convert string to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        s3 = re.sub(r'[^a-zA-Z0-9]', '_', s2)
        return re.sub(r'_+', '_', s3).lower().strip('_')
    
    def _to_camel_case(self, name: str) -> str:
        """Convert string to camelCase"""
        words = re.split(r'[^a-zA-Z0-9]', name)
        words = [word for word in words if word]
        if not words:
            return name
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert string to PascalCase"""
        words = re.split(r'[^a-zA-Z0-9]', name)
        words = [word for word in words if word]
        return ''.join(word.capitalize() for word in words)