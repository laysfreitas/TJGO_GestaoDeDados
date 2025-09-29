from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import io
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configurações para upload
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Apenas arquivos CSV são permitidos'}), 400
    
    try:
        # Ler o conteúdo do arquivo
        content = file.read().decode('utf-8')
        session['csv_content'] = content
        
        # Detectar delimitador automaticamente
        delimiters = [',', ';', '\t', '|']
        delimiter_counts = {}
        
        for delim in delimiters:
            delimiter_counts[delim] = content.count(delim)
        
        # Escolher o delimitador mais comum
        detected_delimiter = max(delimiter_counts, key=delimiter_counts.get)
        
        # Ler CSV com o delimitador detectado
        df = pd.read_csv(io.StringIO(content), delimiter=detected_delimiter)
        
        # Armazenar informações na sessão
        session['detected_delimiter'] = detected_delimiter
        session['columns'] = df.columns.tolist()
        session['data_types'] = df.dtypes.astype(str).to_dict()
        session['sample_data'] = df.head(5).to_dict('records')
        
        return jsonify({
            'success': True,
            'detected_delimiter': detected_delimiter,
            'columns': df.columns.tolist(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'sample_data': df.head(5).to_dict('records'),
            'total_rows': len(df)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao processar arquivo: {str(e)}'}), 400

@app.route('/configure', methods=['POST'])
def configure_data():
    data = request.json
    delimiter = data.get('delimiter', session.get('detected_delimiter', ','))
    
    try:
        # Ler CSV com o delimitador especificado
        content = session.get('csv_content', '')
        df = pd.read_csv(io.StringIO(content), delimiter=delimiter)
        
        # Atualizar sessão
        session['current_delimiter'] = delimiter
        session['columns'] = df.columns.tolist()
        session['data_types'] = df.dtypes.astype(str).to_dict()
        session['sample_data'] = df.head(5).to_dict('records')
        
        return jsonify({
            'success': True,
            'columns': df.columns.tolist(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'sample_data': df.head(5).to_dict('records'),
            'total_rows': len(df)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao reconfigurar dados: {str(e)}'}), 400

@app.route('/process', methods=['POST'])
def process_data():
    data = request.json
    selected_columns = data.get('selected_columns', [])
    column_order = data.get('column_order', [])
    column_formats = data.get('column_formats', {})
    
    try:
        # Ler dados originais
        content = session.get('csv_content', '')
        delimiter = session.get('current_delimiter', ',')
        df = pd.read_csv(io.StringIO(content), delimiter=delimiter)
        
        # Selecionar e reordenar colunas
        if selected_columns:
            df = df[selected_columns]
        
        if column_order:
            # Reordenar colunas conforme especificado
            available_columns = [col for col in column_order if col in df.columns]
            df = df[available_columns]
        
        # Aplicar formatações
        for column, format_info in column_formats.items():
            if column in df.columns:
                format_type = format_info.get('type', 'string')
                
                if format_type == 'date':
                    date_format = format_info.get('format', '%Y-%m-%d')
                    try:
                        df[column] = pd.to_datetime(df[column]).dt.strftime(date_format)
                    except:
                        pass  # Manter original se conversão falhar
                        
                elif format_type == 'number':
                    decimal_places = format_info.get('decimal_places', 2)
                    try:
                        df[column] = pd.to_numeric(df[column]).round(decimal_places)
                    except:
                        pass  # Manter original se conversão falhar
                        
                elif format_type == 'currency':
                    currency_symbol = format_info.get('symbol', 'R$')
                    decimal_places = format_info.get('decimal_places', 2)
                    try:
                        numeric_col = pd.to_numeric(df[column])
                        df[column] = numeric_col.apply(lambda x: f"{currency_symbol} {x:,.{decimal_places}f}")
                    except:
                        pass  # Manter original se conversão falhar
        
        # Armazenar resultado processado
        session['processed_data'] = df.to_dict('records')
        session['processed_columns'] = df.columns.tolist()
        
        return jsonify({
            'success': True,
            'data': df.to_dict('records'),
            'columns': df.columns.tolist(),
            'total_rows': len(df)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao processar dados: {str(e)}'}), 400

@app.route('/export')
def export_data():
    processed_data = session.get('processed_data', [])
    if not processed_data:
        return jsonify({'error': 'Nenhum dado processado disponível'}), 400
    
    # Converter para CSV
    df = pd.DataFrame(processed_data)
    output = io.StringIO()
    df.to_csv(output, index=False)
    csv_content = output.getvalue()
    
    from flask import Response
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=dados_processados.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True)
