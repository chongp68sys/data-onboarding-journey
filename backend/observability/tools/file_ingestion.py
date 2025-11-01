import pandas as pd
from typing import Any, Dict, List, Optional
import os
import struct
from lxml import etree
from bs4 import BeautifulSoup
import chardet
import magic
import openpyxl
import xmltodict
import ebcdic
from pathlib import Path

class FileIngestionTools:
    """Tools for file ingestion and parsing operations"""
    
    def __init__(self, working_directory: str = "tmp"):
        self.working_directory = working_directory
        os.makedirs(working_directory, exist_ok=True)
    
    def detect_file_type(self, file_path: str) -> str:
        """Detect actual file type using python-magic
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            String description of the detected file type
        """
        try:
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
                
            file_type = magic.from_file(file_path)
            return file_type
        except Exception as e:
            # Fallback to extension-based detection
            extension = Path(file_path).suffix.lower()
            type_mapping = {
                '.csv': 'CSV text',
                '.txt': 'ASCII text',
                '.xlsx': 'Microsoft Excel 2007+',
                '.xls': 'Microsoft Excel 97-2003',
                '.json': 'JSON text',
                '.xml': 'XML document',
                '.dat': 'Binary data',
                '.bin': 'Binary data'
            }
            detected = type_mapping.get(extension, 'Unknown file type')
            return f"{detected} (fallback detection due to error: {str(e)})"
    
    def detect_encoding(self, file_path: str) -> str:
        """Detect file encoding using chardet
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Detected encoding string
        """
        try:
            if not os.path.exists(file_path):
                return "utf-8"
                
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                confidence = result.get('confidence', 0)
                encoding = result.get('encoding', 'utf-8')
                
                # If confidence is low, try common encodings
                if confidence < 0.7:
                    for test_encoding in ['utf-8', 'latin-1', 'cp1252', 'cp500']:  # cp500 is EBCDIC
                        try:
                            raw_data.decode(test_encoding)
                            return f"{test_encoding} (tested)"
                        except:
                            continue
                
                return f"{encoding} (confidence: {confidence:.2f})"
        except Exception as e:
            return f"utf-8 (fallback due to error: {str(e)})"
    
    def read_csv_file(self, file_path: str, delimiter: str = ",", encoding: str = None, skip_rows: int = 0) -> str:
        """Read CSV file with pandas and return summary
        
        Args:
            file_path: Path to the CSV file
            delimiter: CSV delimiter (default: comma)
            encoding: File encoding (auto-detect if None)
            skip_rows: Number of rows to skip from the beginning
            
        Returns:
            JSON string with results and metadata
        """
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Auto-detect encoding if not provided
            if not encoding:
                encoding_info = self.detect_encoding(file_path)
                encoding = encoding_info.split()[0]  # Get just the encoding name
            
            # Read CSV
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                delimiter=delimiter,
                skiprows=skip_rows,
                low_memory=False
            )
            
            # Generate summary
            summary = {
                "success": True,
                "file_type": "CSV",
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "encoding_used": encoding,
                "delimiter_used": delimiter,
                "data_types": df.dtypes.to_dict(),
                "sample_data": df.head(3).to_dict('records'),
                "null_counts": df.isnull().sum().to_dict(),
                "memory_usage": f"{df.memory_usage().sum()} bytes"
            }
            
            return str(summary)
            
        except Exception as e:
            return f"Error reading CSV file: {str(e)}"
    
    def read_excel_file(self, file_path: str, sheet_name: str = None, header_row: int = 0) -> str:
        """Read Excel file with pandas and return summary
        
        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name or index (None for first sheet)
            header_row: Row number to use as header
            
        Returns:
            JSON string with results and metadata
        """
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Get sheet info first
            excel_file = pd.ExcelFile(file_path)
            available_sheets = excel_file.sheet_names
            
            if sheet_name is None:
                sheet_name = available_sheets[0]  # Use first sheet
            elif sheet_name not in available_sheets:
                return f"Error: Sheet '{sheet_name}' not found. Available sheets: {available_sheets}"
            
            # Read Excel
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=header_row
            )
            
            # Generate summary
            summary = {
                "success": True,
                "file_type": "Excel",
                "available_sheets": available_sheets,
                "sheet_used": sheet_name,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "sample_data": df.head(3).to_dict('records'),
                "null_counts": df.isnull().sum().to_dict(),
                "memory_usage": f"{df.memory_usage().sum()} bytes"
            }
            
            return str(summary)
            
        except Exception as e:
            return f"Error reading Excel file: {str(e)}"
    
    def read_json_file(self, file_path: str, orient: str = "records", normalize: bool = True) -> str:
        """Read JSON file with pandas and return summary
        
        Args:
            file_path: Path to the JSON file
            orient: JSON orientation (records, index, values, etc.)
            normalize: Whether to normalize nested JSON
            
        Returns:
            JSON string with results and metadata
        """
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Read JSON
            if normalize:
                data = pd.read_json(file_path, orient=orient)
                df = pd.json_normalize(data) if isinstance(data, list) else pd.json_normalize([data])
            else:
                df = pd.read_json(file_path, orient=orient)
            
            # Generate summary
            summary = {
                "success": True,
                "file_type": "JSON",
                "orientation": orient,
                "normalized": normalize,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "sample_data": df.head(3).to_dict('records'),
                "null_counts": df.isnull().sum().to_dict(),
                "memory_usage": f"{df.memory_usage().sum()} bytes"
            }
            
            return str(summary)
            
        except Exception as e:
            return f"Error reading JSON file: {str(e)}"
    
    def read_xml_file(self, file_path: str, xpath: str = None) -> str:
        """Parse XML file and convert to DataFrame
        
        Args:
            file_path: Path to the XML file
            xpath: Optional XPath expression for data extraction
            
        Returns:
            JSON string with results and metadata
        """
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Try different parsing approaches
            parsing_method = "unknown"
            df = pd.DataFrame()
            
            try:
                # Method 1: xmltodict for structured parsing
                xml_dict = xmltodict.parse(content)
                df = pd.json_normalize(xml_dict)
                parsing_method = "xmltodict"
                
                # If too nested, try to flatten
                if len(df.columns) == 1 and len(df) == 1:
                    first_value = df.iloc[0, 0]
                    if isinstance(first_value, dict):
                        df = pd.json_normalize(first_value)
                        parsing_method = "xmltodict (flattened)"
                        
            except Exception:
                try:
                    # Method 2: XPath extraction
                    if xpath:
                        tree = etree.parse(file_path)
                        elements = tree.xpath(xpath)
                        data = [elem.text if elem.text else str(elem) for elem in elements]
                        df = pd.DataFrame(data, columns=['extracted_value'])
                        parsing_method = f"xpath: {xpath}"
                    else:
                        # Method 3: BeautifulSoup fallback
                        soup = BeautifulSoup(content, 'xml')
                        df = self._xml_soup_to_dataframe(soup)
                        parsing_method = "BeautifulSoup"
                        
                except Exception:
                    df = pd.DataFrame([{"error": "Could not parse XML structure"}])
                    parsing_method = "error"
            
            # Generate summary
            summary = {
                "success": len(df) > 0,
                "file_type": "XML",
                "parsing_method": parsing_method,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "sample_data": df.head(3).to_dict('records'),
                "null_counts": df.isnull().sum().to_dict(),
                "memory_usage": f"{df.memory_usage().sum()} bytes"
            }
            
            return str(summary)
            
        except Exception as e:
            return f"Error reading XML file: {str(e)}"
    
    def read_binary_file(self, file_path: str, record_length: int = 80, format_spec: str = None, ebcdic_variant: str = "cp500") -> str:
        """Parse binary/mainframe data files
        
        Args:
            file_path: Path to the binary file
            record_length: Length of each record in bytes
            format_spec: Struct format specification for unpacking
            ebcdic_variant: EBCDIC encoding variant (default: cp500)
            
        Returns:
            JSON string with results and metadata
        """
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            data = []
            conversion_method = "unknown"
            
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(record_length)
                    if not chunk:
                        break
                    
                    try:
                        if format_spec:
                            # Structured unpacking
                            record = struct.unpack(format_spec, chunk)
                            data.append(list(record))
                            conversion_method = f"struct: {format_spec}"
                        else:
                            # EBCDIC conversion attempt
                            try:
                                text_data = chunk.decode(ebcdic_variant)
                                data.append([text_data.strip()])
                                conversion_method = f"EBCDIC: {ebcdic_variant}"
                            except:
                                # Hex fallback
                                data.append([chunk.hex()])
                                conversion_method = "hex_representation"
                    except Exception:
                        # Skip malformed records
                        continue
            
            df = pd.DataFrame(data)
            if df.empty:
                df = pd.DataFrame([{"error": "No readable data found"}])
            
            # Generate summary
            summary = {
                "success": len(data) > 0,
                "file_type": "Binary/Mainframe",
                "conversion_method": conversion_method,
                "record_length": record_length,
                "records_processed": len(data),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "sample_data": df.head(3).to_dict('records'),
                "file_size_bytes": os.path.getsize(file_path)
            }
            
            return str(summary)
            
        except Exception as e:
            return f"Error reading binary file: {str(e)}"
    
    def infer_schema(self, file_path: str) -> str:
        """Analyze a file and infer its schema and characteristics
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            JSON string with schema information
        """
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Basic file info
            file_info = {
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "file_extension": Path(file_path).suffix.lower(),
                "detected_type": self.detect_file_type(file_path),
                "detected_encoding": self.detect_encoding(file_path)
            }
            
            # Try to read a sample and infer structure
            extension = file_info["file_extension"]
            sample_analysis = {}
            
            try:
                if extension in ['.csv', '.txt']:
                    result = self.read_csv_file(file_path)
                elif extension in ['.xlsx', '.xls']:
                    result = self.read_excel_file(file_path)
                elif extension == '.json':
                    result = self.read_json_file(file_path)
                elif extension == '.xml':
                    result = self.read_xml_file(file_path)
                else:
                    result = "Unsupported file type for schema inference"
                
                sample_analysis["parsing_result"] = result
                
            except Exception as e:
                sample_analysis["parsing_error"] = str(e)
            
            schema_info = {
                "file_info": file_info,
                "sample_analysis": sample_analysis,
                "recommendations": self._generate_processing_recommendations(file_info, sample_analysis)
            }
            
            return str(schema_info)
            
        except Exception as e:
            return f"Error inferring schema: {str(e)}"
    
    def _xml_soup_to_dataframe(self, soup: BeautifulSoup) -> pd.DataFrame:
        """Convert XML BeautifulSoup to DataFrame"""
        data = []
        records = soup.find_all(recursive=False)
        
        for record in records[:100]:  # Limit to first 100 records
            row = {}
            for child in record.find_all():
                if child.string:
                    row[child.name] = child.string.strip()
            if row:
                data.append(row)
        
        return pd.DataFrame(data) if data else pd.DataFrame([{"message": "No tabular data found in XML"}])
    
    def _generate_processing_recommendations(self, file_info: dict, sample_analysis: dict) -> list:
        """Generate recommendations for processing the file"""
        recommendations = []
        
        # File size recommendations
        if file_info["file_size"] > 100 * 1024 * 1024:  # > 100MB
            recommendations.append("Large file detected. Consider chunked processing or using Polars for better performance.")
        
        # Encoding recommendations
        if "cp500" in file_info["detected_encoding"]:
            recommendations.append("EBCDIC encoding detected. This appears to be mainframe data.")
        
        # Type-specific recommendations
        extension = file_info["file_extension"]
        if extension == '.csv':
            recommendations.append("For CSV files, consider detecting delimiter and handling quoted fields.")
        elif extension in ['.xlsx', '.xls']:
            recommendations.append("Excel file detected. Check for multiple sheets and merged cells.")
        elif extension == '.xml':
            recommendations.append("XML file detected. Consider XPath expressions for targeted data extraction.")
        
        return recommendations