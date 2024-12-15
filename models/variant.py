
from typing import Dict, Any
from models.variant_display import VariantDisplay

class Variant:
    
    def __init__(self, record: Dict[str, Any]):
        #Inicializar variante del registro VCF
        self.chromosome = record['#CHROM']
        self.position = int(record['POS'])
        self.variant_id = record['ID']
        self.reference = record['REF']
        self.alternative = record['ALT']
        self.quality = record['QUAL']
        self.filter = record['FILTER']
        self.info = record['INFO']
        self.format = record['FORMAT']
        self.samples = self._process_samples(record)
    
    def _process_samples(self, record: Dict[str, Any]) -> Dict[str, str]:
        #Extraer y procesar información de muestra del registro
        return {
            key: record[key]
            for key in record
            if key.startswith('output_')
        }
    
    def to_dict(self) -> Dict[str, Any]:
        #Convertir al formato de documento MongoDB
        return {
            'chromosome': self.chromosome,
            'position': self.position,
            'variant_id': self.variant_id,
            'reference': self.reference,
            'alternative': self.alternative,
            'quality': self.quality,
            'filter': self.filter,
            'info': self.info,
            'format': self.format,
            'samples': self.samples
        }
    
    def to_display_dict(self) -> Dict[str, Any]:
        
        return VariantDisplay.format_for_display(self.to_dict())
    
    @classmethod
    def get_display_columns(cls, variant_dict: Dict[str, Any]) -> list:
       
        return VariantDisplay.get_column_headers(variant_dict)