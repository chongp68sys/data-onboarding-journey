import pandas as pd
import numpy as np
from typing import Dict, List, Any
import re
from datetime import datetime
import os

class DataValidationTools:
    """Tools for data quality assessment and validation"""
    
    def __init__(self, working_directory: str = "tmp"):
        self.working_directory = working_directory
        os.makedirs(working_directory, exist_ok=True)
    
    def analyze_data_quality(self, csv_file_path: str) -> str:
        """Perform comprehensive data quality analysis on a CSV file
        
        Args:
            csv_file_path: Path to the CSV file to analyze
            
        Returns:
            JSON string with detailed quality analysis
        """
        try:
            if not os.path.exists(csv_file_path):
                return f"Error: File not found at {csv_file_path}"
            
            # Read the CSV file
            df = pd.read_csv(csv_file_path, low_memory=False)
            
            total_rows = len(df)
            total_columns = len(df.columns)
            
            # Basic statistics
            basic_stats = {
                "total_rows": total_rows,
                "total_columns": total_columns,
                "empty_dataframe": total_rows == 0,
                "file_size_mb": round(os.path.getsize(csv_file_path) / (1024*1024), 2)
            }
            
            # Completeness analysis
            completeness = {}
            for column in df.columns:
                null_count = df[column].isnull().sum()
                null_percentage = (null_count / total_rows) * 100 if total_rows > 0 else 0
                
                completeness[column] = {
                    "null_count": int(null_count),
                    "null_percentage": round(null_percentage, 2),
                    "completeness_score": round(100 - null_percentage, 2)
                }
            
            # Data type analysis
            data_types = {}
            for column in df.columns:
                dtype = str(df[column].dtype)
                unique_count = df[column].nunique()
                
                # Try to infer better data types
                suggested_type = self._suggest_data_type(df[column])
                
                data_types[column] = {
                    "current_type": dtype,
                    "suggested_type": suggested_type,
                    "unique_values": int(unique_count),
                    "uniqueness_ratio": round(unique_count / total_rows, 3) if total_rows > 0 else 0,
                    "sample_values": df[column].dropna().head(3).tolist()
                }
            
            # Consistency analysis
            consistency = {}
            for column in df.columns:
                if df[column].dtype == 'object':
                    # Check for inconsistent formatting
                    non_null_values = df[column].dropna().astype(str)
                    if len(non_null_values) > 0:
                        # Check for potential case inconsistencies
                        original_unique = len(non_null_values.unique())
                        normalized_unique = len(non_null_values.str.lower().str.strip().unique())
                        
                        consistency[column] = {
                            "original_unique_values": original_unique,
                            "normalized_unique_values": normalized_unique,
                            "potential_inconsistencies": original_unique - normalized_unique,
                            "consistency_score": round(normalized_unique / original_unique, 3) if original_unique > 0 else 1.0
                        }
            
            # Calculate overall quality score
            overall_score = self._calculate_overall_quality_score(completeness, consistency, data_types)
            
            result = {
                "success": True,
                "file_analyzed": csv_file_path,
                "analysis_timestamp": datetime.now().isoformat(),
                "basic_statistics": basic_stats,
                "completeness_analysis": completeness,
                "data_type_analysis": data_types,
                "consistency_analysis": consistency,
                "overall_quality_score": overall_score,
                "recommendations": self._generate_quality_recommendations(completeness, consistency, data_types)
            }
            
            return str(result)
            
        except Exception as e:
            return f"Error analyzing data quality: {str(e)}"
    
    def detect_duplicates(self, csv_file_path: str, key_columns: str = None) -> str:
        """Detect duplicate records in a CSV file
        
        Args:
            csv_file_path: Path to the CSV file
            key_columns: Comma-separated list of columns to check for duplicates (optional)
            
        Returns:
            JSON string with duplicate analysis
        """
        try:
            if not os.path.exists(csv_file_path):
                return f"Error: File not found at {csv_file_path}"
            
            df = pd.read_csv(csv_file_path, low_memory=False)
            
            # Full row duplicates
            full_duplicates = df.duplicated()
            full_duplicate_count = full_duplicates.sum()
            
            duplicate_analysis = {
                "total_rows": len(df),
                "full_row_duplicates": {
                    "count": int(full_duplicate_count),
                    "percentage": round((full_duplicate_count / len(df)) * 100, 2) if len(df) > 0 else 0,
                    "duplicate_indices": df.index[full_duplicates].tolist()[:10]  # First 10 indices
                }
            }
            
            # Key column duplicates if specified
            if key_columns:
                key_cols = [col.strip() for col in key_columns.split(',')]
                available_cols = [col for col in key_cols if col in df.columns]
                
                if available_cols:
                    key_duplicates = df.duplicated(subset=available_cols)
                    key_duplicate_count = key_duplicates.sum()
                    
                    # Get examples of duplicate values
                    if key_duplicate_count > 0:
                        duplicate_examples = df[key_duplicates][available_cols].head(5).to_dict('records')
                    else:
                        duplicate_examples = []
                    
                    duplicate_analysis["key_column_duplicates"] = {
                        "key_columns": available_cols,
                        "count": int(key_duplicate_count),
                        "percentage": round((key_duplicate_count / len(df)) * 100, 2) if len(df) > 0 else 0,
                        "duplicate_examples": duplicate_examples
                    }
                else:
                    duplicate_analysis["key_column_duplicates"] = {
                        "error": f"None of the specified key columns found: {key_cols}"
                    }
            
            result = {
                "success": True,
                "file_analyzed": csv_file_path,
                "duplicate_analysis": duplicate_analysis,
                "recommendations": self._generate_duplicate_recommendations(duplicate_analysis)
            }
            
            return str(result)
            
        except Exception as e:
            return f"Error detecting duplicates: {str(e)}"
    
    def validate_data_patterns(self, csv_file_path: str, pattern_rules: str) -> str:
        """Validate data against regex patterns
        
        Args:
            csv_file_path: Path to the CSV file
            pattern_rules: JSON string with pattern validation rules
            
        Returns:
            JSON string with pattern validation results
        """
        try:
            if not os.path.exists(csv_file_path):
                return f"Error: File not found at {csv_file_path}"
            
            import json
            
            # Parse pattern rules
            try:
                rules = json.loads(pattern_rules)
            except:
                rules = eval(pattern_rules)
            
            df = pd.read_csv(csv_file_path, low_memory=False)
            
            validation_results = {}
            
            for column, pattern_config in rules.items():
                if column not in df.columns:
                    validation_results[column] = {"error": f"Column '{column}' not found"}
                    continue
                
                pattern = pattern_config.get("pattern", "")
                description = pattern_config.get("description", "Custom pattern")
                
                if not pattern:
                    validation_results[column] = {"error": "No pattern specified"}
                    continue
                
                # Convert column to string and handle nulls
                column_data = df[column].fillna("").astype(str)
                
                # Check pattern matches
                try:
                    matches = column_data.str.match(pattern, na=False)
                    match_count = matches.sum()
                    total_count = len(column_data)
                    
                    # Get examples of non-matching values
                    non_matches = column_data[~matches]
                    non_match_examples = non_matches.head(5).tolist()
                    
                    validation_results[column] = {
                        "pattern": pattern,
                        "description": description,
                        "total_values": total_count,
                        "matching_values": int(match_count),
                        "match_percentage": round((match_count / total_count) * 100, 2) if total_count > 0 else 0,
                        "violations": total_count - match_count,
                        "violation_examples": [val for val in non_match_examples if val]  # Remove empty strings
                    }
                    
                except Exception as pattern_error:
                    validation_results[column] = {"error": f"Pattern validation failed: {str(pattern_error)}"}
            
            result = {
                "success": True,
                "file_analyzed": csv_file_path,
                "pattern_validation_results": validation_results,
                "summary": {
                    "columns_validated": len([col for col, res in validation_results.items() if "error" not in res]),
                    "total_violations": sum(res.get("violations", 0) for res in validation_results.values() if isinstance(res, dict))
                }
            }
            
            return str(result)
            
        except Exception as e:
            return f"Error validating data patterns: {str(e)}"
    
    def detect_outliers(self, csv_file_path: str, numeric_columns: str = None, method: str = "iqr", threshold: float = 1.5) -> str:
        """Detect statistical outliers in numeric columns
        
        Args:
            csv_file_path: Path to the CSV file
            numeric_columns: Comma-separated list of numeric columns (optional, analyzes all if not specified)
            method: Detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            JSON string with outlier analysis
        """
        try:
            if not os.path.exists(csv_file_path):
                return f"Error: File not found at {csv_file_path}"
            
            df = pd.read_csv(csv_file_path, low_memory=False)
            
            # Determine columns to analyze
            if numeric_columns:
                columns_to_analyze = [col.strip() for col in numeric_columns.split(',') if col.strip() in df.columns]
            else:
                columns_to_analyze = df.select_dtypes(include=[np.number]).columns.tolist()
            
            outlier_results = {}
            
            for column in columns_to_analyze:
                column_data = pd.to_numeric(df[column], errors='coerce').dropna()
                
                if len(column_data) == 0:
                    outlier_results[column] = {"error": "No valid numeric data found"}
                    continue
                
                # Detect outliers based on method
                if method == "iqr":
                    outliers = self._detect_iqr_outliers(column_data, threshold)
                elif method == "zscore":
                    outliers = self._detect_zscore_outliers(column_data, threshold)
                else:
                    outliers = self._detect_iqr_outliers(column_data, threshold)
                
                # Calculate statistics
                stats = {
                    "count": len(column_data),
                    "mean": float(column_data.mean()),
                    "std": float(column_data.std()),
                    "min": float(column_data.min()),
                    "max": float(column_data.max()),
                    "q1": float(column_data.quantile(0.25)),
                    "median": float(column_data.median()),
                    "q3": float(column_data.quantile(0.75))
                }
                
                outlier_results[column] = {
                    "method": method,
                    "threshold": threshold,
                    "statistics": stats,
                    "outliers_found": len(outliers["values"]),
                    "outlier_percentage": round((len(outliers["values"]) / len(column_data)) * 100, 2),
                    "outlier_values": outliers["values"][:10],  # First 10 outlier values
                    "outlier_indices": outliers["indices"][:10]  # First 10 indices
                }
            
            result = {
                "success": True,
                "file_analyzed": csv_file_path,
                "outlier_analysis": outlier_results,
                "method_used": method,
                "threshold_used": threshold,
                "columns_analyzed": columns_to_analyze
            }
            
            return str(result)
            
        except Exception as e:
            return f"Error detecting outliers: {str(e)}"
    
    def generate_data_report(self, csv_file_path: str) -> str:
        """Generate a comprehensive data quality report
        
        Args:
            csv_file_path: Path to the CSV file
            
        Returns:
            JSON string with comprehensive report
        """
        try:
            if not os.path.exists(csv_file_path):
                return f"Error: File not found at {csv_file_path}"
            
            # Combine multiple analyses
            quality_analysis = self.analyze_data_quality(csv_file_path)
            duplicate_analysis = self.detect_duplicates(csv_file_path)
            outlier_analysis = self.detect_outliers(csv_file_path)
            
            # Parse results
            import ast
            
            try:
                quality_result = ast.literal_eval(quality_analysis)
                duplicate_result = ast.literal_eval(duplicate_analysis)
                outlier_result = ast.literal_eval(outlier_analysis)
            except:
                return f"Error: Could not parse analysis results"
            
            # Generate executive summary
            executive_summary = {
                "file_name": os.path.basename(csv_file_path),
                "analysis_date": datetime.now().isoformat(),
                "data_dimensions": {
                    "rows": quality_result.get("basic_statistics", {}).get("total_rows", 0),
                    "columns": quality_result.get("basic_statistics", {}).get("total_columns", 0)
                },
                "overall_quality_score": quality_result.get("overall_quality_score", 0),
                "critical_issues": []
            }
            
            # Identify critical issues
            if duplicate_result.get("duplicate_analysis", {}).get("full_row_duplicates", {}).get("count", 0) > 0:
                executive_summary["critical_issues"].append("Duplicate rows detected")
            
            # Check for high null percentages
            completeness = quality_result.get("completeness_analysis", {})
            high_null_columns = [col for col, info in completeness.items() if info.get("null_percentage", 0) > 50]
            if high_null_columns:
                executive_summary["critical_issues"].append(f"High null percentages in columns: {', '.join(high_null_columns[:3])}")
            
            # Check for outliers
            outlier_data = outlier_result.get("outlier_analysis", {})
            outlier_columns = [col for col, info in outlier_data.items() if info.get("outliers_found", 0) > 0]
            if outlier_columns:
                executive_summary["critical_issues"].append(f"Statistical outliers detected in {len(outlier_columns)} columns")
            
            comprehensive_report = {
                "success": True,
                "executive_summary": executive_summary,
                "detailed_analyses": {
                    "data_quality": quality_result,
                    "duplicate_detection": duplicate_result,
                    "outlier_detection": outlier_result
                },
                "recommendations": self._generate_comprehensive_recommendations(
                    quality_result, duplicate_result, outlier_result
                )
            }
            
            return str(comprehensive_report)
            
        except Exception as e:
            return f"Error generating data report: {str(e)}"
    
    def _suggest_data_type(self, series: pd.Series) -> str:
        """Suggest optimal data type for a pandas Series"""
        try:
            # Skip if all null
            if series.isnull().all():
                return str(series.dtype)
            
            # Try datetime conversion
            try:
                pd.to_datetime(series.dropna(), errors='raise')
                return "datetime64[ns]"
            except:
                pass
            
            # Try numeric conversion
            try:
                numeric_series = pd.to_numeric(series.dropna(), errors='raise')
                if (numeric_series % 1 == 0).all():
                    return "int64"
                else:
                    return "float64"
            except:
                pass
            
            # Check for boolean
            unique_values = series.dropna().unique()
            if len(unique_values) <= 2:
                str_values = [str(val).lower() for val in unique_values]
                if all(val in ['true', 'false', '1', '0', 'yes', 'no', 't', 'f'] for val in str_values):
                    return "bool"
            
            # Check for category
            if len(unique_values) < len(series) * 0.1:  # Less than 10% unique values
                return "category"
            
            return "object"
            
        except:
            return str(series.dtype)
    
    def _calculate_overall_quality_score(self, completeness: dict, consistency: dict, data_types: dict) -> float:
        """Calculate overall data quality score"""
        try:
            scores = []
            
            # Completeness score
            if completeness:
                completeness_scores = [info.get("completeness_score", 0) for info in completeness.values()]
                scores.append(sum(completeness_scores) / len(completeness_scores))
            
            # Consistency score
            if consistency:
                consistency_scores = [info.get("consistency_score", 1) * 100 for info in consistency.values()]
                scores.append(sum(consistency_scores) / len(consistency_scores))
            
            # Data type alignment score (simplified)
            if data_types:
                type_scores = []
                for info in data_types.values():
                    if info.get("current_type") == info.get("suggested_type"):
                        type_scores.append(100)
                    else:
                        type_scores.append(80)  # Partial credit for convertible types
                scores.append(sum(type_scores) / len(type_scores))
            
            return round(sum(scores) / len(scores), 1) if scores else 0.0
            
        except:
            return 0.0
    
    def _generate_quality_recommendations(self, completeness: dict, consistency: dict, data_types: dict) -> list:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        # Completeness recommendations
        for column, info in completeness.items():
            if info.get("null_percentage", 0) > 20:
                recommendations.append(f"High null percentage ({info['null_percentage']}%) in column '{column}' - consider imputation or removal")
        
        # Consistency recommendations
        for column, info in consistency.items():
            if info.get("potential_inconsistencies", 0) > 0:
                recommendations.append(f"Inconsistent formatting detected in column '{column}' - consider standardization")
        
        # Data type recommendations
        for column, info in data_types.items():
            if info.get("current_type") != info.get("suggested_type"):
                recommendations.append(f"Column '{column}' could be converted from {info['current_type']} to {info['suggested_type']}")
        
        return recommendations
    
    def _generate_duplicate_recommendations(self, duplicate_analysis: dict) -> list:
        """Generate duplicate handling recommendations"""
        recommendations = []
        
        full_duplicates = duplicate_analysis.get("full_row_duplicates", {}).get("count", 0)
        if full_duplicates > 0:
            recommendations.append(f"Remove {full_duplicates} duplicate rows to improve data quality")
        
        key_duplicates = duplicate_analysis.get("key_column_duplicates", {}).get("count", 0)
        if key_duplicates > 0:
            recommendations.append("Key column duplicates detected - review data integrity rules")
        
        return recommendations
    
    def _generate_comprehensive_recommendations(self, quality_result: dict, duplicate_result: dict, outlier_result: dict) -> list:
        """Generate comprehensive recommendations from all analyses"""
        recommendations = []
        
        # Quality recommendations
        if quality_result.get("success"):
            recommendations.extend(quality_result.get("recommendations", []))
        
        # Duplicate recommendations
        if duplicate_result.get("success"):
            recommendations.extend(duplicate_result.get("recommendations", []))
        
        # Outlier recommendations
        outlier_data = outlier_result.get("outlier_analysis", {})
        for column, info in outlier_data.items():
            if isinstance(info, dict) and info.get("outliers_found", 0) > 0:
                recommendations.append(f"Review {info['outliers_found']} outliers in column '{column}'")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _detect_iqr_outliers(self, series: pd.Series, threshold: float) -> dict:
        """Detect outliers using IQR method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        
        return {
            "indices": outliers.index.tolist(),
            "values": outliers.tolist()
        }
    
    def _detect_zscore_outliers(self, series: pd.Series, threshold: float) -> dict:
        """Detect outliers using Z-score method"""
        z_scores = np.abs((series - series.mean()) / series.std())
        outliers = series[z_scores > threshold]
        
        return {
            "indices": outliers.index.tolist(),
            "values": outliers.tolist()
        }