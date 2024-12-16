from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class VariantDisplayFields:
    
    CHROM = 'Chromosome'
    POS = 'Position'
    ID = 'Identifier'
    REF = 'Reference'
    ALT = 'Alternative'
    QUAL = 'Quality'
    FILTER = 'Filter'
    INFO = 'Information'
    FORMAT = 'Format'
    
    @classmethod
    def get_base_columns(cls) -> list:
        
        return [
            cls.CHROM,
            cls.POS,
            cls.ID,
            cls.REF,
            cls.ALT,
            cls.QUAL,
            cls.FILTER,
            cls.INFO,
            cls.FORMAT
        ]

class VariantDisplay:
    
    
    @staticmethod
    def format_for_display(variant_dict: Dict[str, Any]) -> Dict[str, Any]:
        
        display_data = {
            VariantDisplayFields.CHROM: variant_dict['chromosome'],
            VariantDisplayFields.POS: variant_dict['position'],
            VariantDisplayFields.ID: variant_dict['variant_id'],
            VariantDisplayFields.REF: variant_dict['reference'],
            VariantDisplayFields.ALT: variant_dict['alternative'],
            VariantDisplayFields.QUAL: variant_dict['quality'],
            VariantDisplayFields.FILTER: variant_dict['filter'],
            VariantDisplayFields.INFO: variant_dict['info'],
            VariantDisplayFields.FORMAT: variant_dict['format']
        }
        
        # Add sample outputs dynamically
        for sample_key, sample_value in variant_dict['samples'].items():
            display_data[sample_key] = sample_value
            
        return display_data
    
    @staticmethod
    def get_column_headers(variant_dict: Dict[str, Any]) -> list:
        
        base_columns = VariantDisplayFields.get_base_columns()
        sample_columns = sorted(variant_dict['samples'].keys())
        return base_columns + sample_columns