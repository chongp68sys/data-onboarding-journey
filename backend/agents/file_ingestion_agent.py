import pandas as pd
import polars as pl
from typing import Any, Dict, List
import os
import struct
from lxml import etree
from bs4 import BeautifulSoup
import io
import chardet
from .base_agent import BaseAgent, AgentTool, AgentResult

class FileIngestionAgent(BaseAgent):
    """Agent responsible for reading and parsing incoming data files"""
    
    def __init__(self):
        super().__init__(
            name="file_ingestion_agent",
            description="Reads and parses various file formats with schema inference"
        )
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools for file ingestion"""
        tools = [
            AgentTool(
                name="read_csv",
                description="Read CSV files with configurable parameters",
                parameters={
                    "file_path": "str",
                    "delimiter": "str",
                    "encoding": "str",
                    "skip_rows": "int"
                }
            ),
            AgentTool(
                name="read_excel",
                description="Read Excel files with sheet selection",
                parameters={
                    "file_path": "str",
                    "sheet_name": "str",
                    "header_row": "int"
                }
            ),
            AgentTool(
                name="read_json",
                description="Read JSON files with nested object handling",
                parameters={
                    "file_path": "str",
                    "orient": "str",
                    "normalize": "bool"
                }
            ),
            AgentTool(
                name="read_xml",
                description="Parse XML files and convert to tabular format",
                parameters={
                    "file_path": "str",
                    "xpath": "str",
                    "namespaces": "dict"
                }
            ),
            AgentTool(
                name="read_fixed_width",
                description="Read fixed-width text files (mainframe exports)",
                parameters={
                    "file_path": "str",
                    "column_specs": "list",
                    "encoding": "str"
                }
            ),
            AgentTool(
                name="read_binary",
                description="Parse binary mainframe data files",
                parameters={
                    "file_path": "str",
                    "format_spec": "str",
                    "record_length": "int"
                }
            ),
            AgentTool(
                name="detect_encoding",
                description="Detect file encoding automatically",
                parameters={"file_path": "str"}
            ),
            AgentTool(
                name="infer_schema",
                description="Automatically infer data types and schema",
                parameters={"dataframe": "pandas.DataFrame"}
            )
        ]
        
        for tool in tools:
            self.register_tool(tool)
    
    def get_available_tools(self) -> List[AgentTool]:
        return self.tools
    
    async def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Execute file ingestion task"""
        try:
            file_path = context.get("file_path")
            if not file_path or not os.path.exists(file_path):
                return AgentResult(
                    success=False,
                    error="File path not provided or file does not exist"
                )
            
            # Detect file type and use appropriate reader
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension in ['.csv', '.txt']:
                result = await self._read_csv_file(file_path, context)
            elif file_extension in ['.xlsx', '.xls']:
                result = await self._read_excel_file(file_path, context)
            elif file_extension == '.json':
                result = await self._read_json_file(file_path, context)
            elif file_extension == '.xml':
                result = await self._read_xml_file(file_path, context)
            elif file_extension in ['.dat', '.bin']:
                result = await self._read_binary_file(file_path, context)
            else:
                # Try to auto-detect format
                result = await self._auto_detect_format(file_path, context)
            
            return result
            
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"File ingestion failed: {str(e)}"
            )
    
    async def _read_csv_file(self, file_path: str, context: Dict[str, Any]) -> AgentResult:
        """Read CSV file with pandas"""
        try:
            # Detect encoding if not provided
            encoding = context.get("encoding")
            if not encoding:
                encoding = await self._detect_encoding(file_path)
            
            # Read CSV with pandas
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                delimiter=context.get("delimiter", ","),
                skiprows=context.get("skip_rows", 0),
                low_memory=False
            )
            
            # Infer schema
            schema_info = await self._infer_schema(df)
            
            return AgentResult(
                success=True,
                data=df,
                metadata={
                    "rows": len(df),
                    "columns": len(df.columns),
                    "schema": schema_info,
                    "encoding": encoding,
                    "file_type": "csv"
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"CSV reading failed: {str(e)}"
            )
    
    async def _read_excel_file(self, file_path: str, context: Dict[str, Any]) -> AgentResult:
        """Read Excel file with pandas"""
        try:
            sheet_name = context.get("sheet_name", 0)  # First sheet by default
            
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=context.get("header_row", 0)
            )
            
            schema_info = await self._infer_schema(df)
            
            return AgentResult(
                success=True,
                data=df,
                metadata={
                    "rows": len(df),
                    "columns": len(df.columns),
                    "schema": schema_info,
                    "sheet_name": sheet_name,
                    "file_type": "excel"
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Excel reading failed: {str(e)}"
            )
    
    async def _read_json_file(self, file_path: str, context: Dict[str, Any]) -> AgentResult:
        """Read JSON file with pandas"""
        try:
            orient = context.get("orient", "records")
            normalize = context.get("normalize", True)
            
            if normalize:
                df = pd.json_normalize(pd.read_json(file_path, orient=orient))
            else:
                df = pd.read_json(file_path, orient=orient)
            
            schema_info = await self._infer_schema(df)
            
            return AgentResult(
                success=True,
                data=df,
                metadata={
                    "rows": len(df),
                    "columns": len(df.columns),
                    "schema": schema_info,
                    "file_type": "json"
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"JSON reading failed: {str(e)}"
            )
    
    async def _read_xml_file(self, file_path: str, context: Dict[str, Any]) -> AgentResult:
        """Parse XML file and convert to DataFrame"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Use BeautifulSoup for flexible XML parsing
            soup = BeautifulSoup(content, 'xml')
            
            # Extract data based on context or auto-detect structure
            xpath = context.get("xpath")
            if xpath:
                # Use lxml for xpath queries
                tree = etree.parse(file_path)
                elements = tree.xpath(xpath)
                data = [elem.text for elem in elements]
                df = pd.DataFrame(data, columns=['value'])
            else:
                # Auto-detect tabular structure
                df = self._xml_to_dataframe(soup)
            
            schema_info = await self._infer_schema(df)
            
            return AgentResult(
                success=True,
                data=df,
                metadata={
                    "rows": len(df),
                    "columns": len(df.columns),
                    "schema": schema_info,
                    "file_type": "xml"
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"XML parsing failed: {str(e)}"
            )
    
    async def _read_binary_file(self, file_path: str, context: Dict[str, Any]) -> AgentResult:
        """Parse binary mainframe data files"""
        try:
            format_spec = context.get("format_spec", "")
            record_length = context.get("record_length", 0)
            
            data = []
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(record_length)
                    if not chunk:
                        break
                    
                    # Unpack binary data based on format specification
                    if format_spec:
                        record = struct.unpack(format_spec, chunk)
                        data.append(record)
                    else:
                        # Convert EBCDIC to ASCII if needed
                        try:
                            text_data = chunk.decode('cp500')  # EBCDIC encoding
                            data.append([text_data])
                        except:
                            # Fallback to hex representation
                            data.append([chunk.hex()])
            
            df = pd.DataFrame(data)
            schema_info = await self._infer_schema(df)
            
            return AgentResult(
                success=True,
                data=df,
                metadata={
                    "rows": len(df),
                    "columns": len(df.columns),
                    "schema": schema_info,
                    "file_type": "binary",
                    "record_length": record_length
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Binary file parsing failed: {str(e)}"
            )
    
    async def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding using chardet"""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8')
        except:
            return 'utf-8'  # Default fallback
    
    async def _infer_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Infer schema information from DataFrame"""
        schema = {}
        for column in df.columns:
            dtype = str(df[column].dtype)
            null_count = df[column].isnull().sum()
            unique_count = df[column].nunique()
            
            schema[column] = {
                "dtype": dtype,
                "null_count": int(null_count),
                "unique_count": int(unique_count),
                "sample_values": df[column].dropna().head(5).tolist()
            }
        
        return schema
    
    def _xml_to_dataframe(self, soup: BeautifulSoup) -> pd.DataFrame:
        """Convert XML structure to DataFrame"""
        # Simple implementation - can be enhanced based on XML structure
        data = []
        
        # Find all elements that could represent records
        records = soup.find_all(recursive=False)
        
        for record in records[:100]:  # Limit to first 100 records for preview
            row = {}
            for child in record.find_all():
                if child.string:
                    row[child.name] = child.string.strip()
            if row:
                data.append(row)
        
        return pd.DataFrame(data) if data else pd.DataFrame()
    
    async def _auto_detect_format(self, file_path: str, context: Dict[str, Any]) -> AgentResult:
        """Auto-detect file format and parse accordingly"""
        try:
            # Try reading as CSV first
            encoding = await self._detect_encoding(file_path)
            
            # Test different delimiters
            delimiters = [',', ';', '\t', '|']
            
            for delimiter in delimiters:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter, nrows=10)
                    if len(df.columns) > 1:  # Successfully parsed with multiple columns
                        # Read full file
                        df_full = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
                        schema_info = await self._infer_schema(df_full)
                        
                        return AgentResult(
                            success=True,
                            data=df_full,
                            metadata={
                                "rows": len(df_full),
                                "columns": len(df_full.columns),
                                "schema": schema_info,
                                "encoding": encoding,
                                "delimiter": delimiter,
                                "file_type": "auto_detected_csv"
                            }
                        )
                except:
                    continue
            
            # If CSV parsing fails, try fixed-width
            try:
                df = pd.read_fwf(file_path, encoding=encoding)
                schema_info = await self._infer_schema(df)
                
                return AgentResult(
                    success=True,
                    data=df,
                    metadata={
                        "rows": len(df),
                        "columns": len(df.columns),
                        "schema": schema_info,
                        "encoding": encoding,
                        "file_type": "fixed_width"
                    }
                )
            except:
                pass
            
            return AgentResult(
                success=False,
                error="Could not auto-detect file format"
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Auto-detection failed: {str(e)}"
            )