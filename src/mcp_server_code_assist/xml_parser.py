import xml.etree.ElementTree as ET
from pathlib import Path
import xmlschema
import re

class XMLProcessor:
    def __init__(self):
        schema_path = Path(__file__).parent / "schema.xsd"
        self.validator = xmlschema.XMLSchema(schema_path)

    def _normalize_text(self, text: str) -> str:
        """Normalize whitespace in text content"""
        return re.sub(r'\s+', ' ', text).strip()

    def parse(self, xml_str: str) -> dict[str, str | dict[str, str]]:
        root = ET.fromstring(self._normalize_text(xml_str))
        self.validator.validate(root)
        
        result = {
            "function": self._normalize_text(root.find("function").text),
            "path": self._normalize_text(root.find("path").text),
        }

        if (content_elem := root.find("content")) is not None:
            result["content"] = self._normalize_text(content_elem.text)
            
        if (replacements_elem := root.find("replacements")) is not None:
            result["replacements"] = {
                elem.tag: self._normalize_text(elem.text)
                for elem in replacements_elem
            }
            
        return result

    def generate(self, data: dict[str, str | dict[str, str]]) -> str:
        root = ET.Element("instruction")
        ET.SubElement(root, "function").text = data["function"]
        ET.SubElement(root, "path").text = data["path"]
        
        if "content" in data:
            ET.SubElement(root, "content").text = data["content"]
            
        if "replacements" in data:
            replacements = ET.SubElement(root, "replacements")
            for key, value in data["replacements"].items():
                ET.SubElement(replacements, key).text = value
                
        return f'<?xml version="1.0"?>\n{ET.tostring(root, encoding="unicode")}'