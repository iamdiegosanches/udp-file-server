from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
import client 
import os

app = Flask(__name__)
app.secret_key = 'segredo'
UPLOAD_TEMP = "temp"
DOWNLOAD_FOLDER = "download"
os.makedirs(UPLOAD_TEMP, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    try:
        arquivos = client.list()
        arquivo_link = session.pop('arquivo_para_baixar', None)
    except Exception as e:
        flash(f"Erro ao conectar com o servidor UDP: {e}", "error")
        arquivos = {}
        arquivo_link = None
    return render_template('index.html', arquivos=arquivos, arquivo_para_baixar=arquivo_link)

@app.route('/iniciar-download/<int:index>', methods=['POST'])
def iniciar_download(index):
    try:
        flash("Iniciando download...", "info")

        nome = client.download(index, pasta_destino=DOWNLOAD_FOLDER)
        caminho = os.path.join(DOWNLOAD_FOLDER, f"baixado_{nome}")

        if nome is None or not os.path.exists(caminho):
            flash("Download falhou ou arquivo ausente.", "error")
        else:
            tamanho = os.path.getsize(caminho)
            if tamanho == 0:
                flash("Download falhou: arquivo vazio.", "error")
            else:
                flash(f"Download concluído ({tamanho} bytes).", "success")
                session['arquivo_para_baixar'] = nome
                session.modified = True

    except Exception as e:
        flash(f"Erro no download: {e}", "error")

    return redirect(url_for('index'))

@app.route('/download/<nome>')
def download(nome):
    caminho = os.path.join(DOWNLOAD_FOLDER, f"baixado_{nome}")
    if os.path.exists(caminho):
        return send_file(caminho, as_attachment=True)
    flash("Arquivo não encontrado.", "error")
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        senha = request.form['senha']
        arquivo = request.files['arquivo']

        if not arquivo:
            flash("Nenhum arquivo selecionado.", "error")
            return redirect(request.url)

        caminho = os.path.join(UPLOAD_TEMP, arquivo.filename)
        arquivo.save(caminho)

        try:
            client.send(caminho, senha)
            flash(f"Arquivo '{arquivo.filename}' enviado com sucesso.", "success")
        except Exception as e:
            flash(f"Erro ao enviar arquivo: {e}", "error")
        finally:
            if os.path.exists(caminho):
                os.remove(caminho)
        return redirect(url_for('index'))

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)