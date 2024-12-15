#
class VCFParser:
    # define los encabezados para los archivos 
    HEADER_FORMATS = {
        'CS': [
            '#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT',
            'output_CS1', 'output_CS12', 'output_CS14', 'output_CS15', 'output_CS16',
            'output_CS17', 'output_CS18', 'output_CS19', 'output_CS20', 'output_CS21',
            'output_CS22', 'output_CS23', 'output_CS24', 'output_CS25', 'output_CS3',
            'output_CS4', 'output_CS5', 'output_CS6', 'output_CS7', 'output_CS8',
            'output_CS9'
        ],
        'CH': [
            '#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT',
            'output_CH1', 'output_CH10', 'output_CH11', 'output_CH12', 'output_CH13',
            'output_CH14', 'output_CH15', 'output_CH16', 'output_CH17', 'output_CH18',
            'output_CH19', 'output_CH2', 'output_CH20', 'output_CH3', 'output_CH4',
            'output_CH5', 'output_CH6', 'output_CH7', 'output_CH8', 'output_CH9'
        ]
    }

    @staticmethod
    def is_metadata_line(line):
        #Comprueba si la linea empieza con :## para despues omitirla 
        return line.startswith('##')

    @staticmethod
    def is_header_line(line):
        #verifica si la linea comienza con #chorm
        return line.startswith('#CHROM')

    @staticmethod
    def detect_header_format(header_line):
        #Detectar qué formato de encabezado coincide con el archivo
        header_fields = header_line.strip().split('\t')
        
        for format_name, expected_headers in VCFParser.HEADER_FORMATS.items():
            if header_fields == expected_headers:
                return format_name, expected_headers
        
        return None, None

    @staticmethod
    def process_line(line, headers, line_number):
        #procesar una linea de datos y devolver campos como un diccionario
        fields = line.strip().split('\t')
        if len(fields) != len(headers):
            print(f"Line {line_number}: Found {len(fields)} fields, expected {len(headers)}")
            return None
        return dict(zip(headers, fields))

    @classmethod
    def parse_file(cls, filename):
        #Analizar el archivo VCF y devolver la lista de registros"
        valid_records = []
        header_found = False
        line_number = 0
        current_headers = None
        format_type = None

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                print(f"\nStarting to parse {filename}")
                
                for line in file:
                    line_number += 1
                    
                    if not line.strip():
                        continue
                    
                    if cls.is_metadata_line(line):
                        continue
                    
                    if cls.is_header_line(line):
                        format_type, current_headers = cls.detect_header_format(line)
                        if format_type:
                            header_found = True
                            print(f"\nDetected format type: {format_type}")
                            print(f"Header validation successful!")
                        else:
                            print("\nWARNING: Unknown header format!")
                            print(f"Header line: {line.strip()}")
                        continue
                    
                    if not header_found:
                        continue
                    
                    record = cls.process_line(line, current_headers, line_number)
                    if record:
                        valid_records.append(record)

            print(f"\nParsing completed:")
            print(f"- Format type: {format_type}")
            print(f"- Total lines processed: {line_number}")
            print(f"- Valid records found: {len(valid_records)}")
            
            return valid_records

        except FileNotFoundError:
            print(f"\nError: File '{filename}' not found")
            return []
        except Exception as e:
            print(f"\nError processing file at line {line_number}: {str(e)}")
            return []