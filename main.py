from uu import decode

from flask import Flask, render_template, request, flash, redirect, url_for, session, send_file
import fdb
from flask_bcrypt import Bcrypt
from fpdf import FPDF

app = Flask(__name__)
bcrypt= Bcrypt(app)

app.config['SECRET_KEY'] = 'Chavesdfglkjhgfdscfghjkjhgfdcvbmnb'

host = "localhost"
database = r"D:\LAIS\BANCOMADU\BANCO.FDB"
user = "sysdba"
password = "sysdba"

con = fdb.connect(host=host, database=database, user=user, password=password)

def senha_forte(senha):
    if len(senha) <8:
        return False
    elif senha == senha.lower():
        return False
    elif senha == senha.upper():
        return False
    elif senha == senha.isalpha():
        return False
    elif senha == senha.isdigit():
        return False
    else:
        return True

@app.route('/')
def index():
    return render_template('login.html')
@app.route("/acervo")
def acervo():
    cursor = con.cursor() #abrir o cursor

    cursor.execute("""SELECT l.id_livro, l.NOME, l.AUTOR, l.ANO_PUBLICACAO 
                      FROM LIVROS l 
                        order by l.nome""")
    livros = cursor.fetchall() #fetchall pega tds os dados da tabela e insere na lista livros

    cursor.close() #fecha o cursor

    return render_template('index.html', livros=livros)

@app.route("/novo")
def novo():
    if 'id_usuario' not in session:
        flash('Precisa estar logado')
        return redirect(url_for('login'))
    else:
        return render_template('novo.html')


@app.route('/criar', methods=['POST'])
def criar():
    print('entreu')
    nome = request.form['nome']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']

    cursor = con.cursor()

    try:
        cursor.execute(""" SELECT 1 FROM LIVROS l WHERE nome = ? """, (nome,))
        if cursor.fetchone():
            flash('Erro: livro já cadastrado', 'error')
            return redirect(url_for('novo'))
        cursor.execute("""INSERT INTO livros (nome, autor, ANO_PUBLICACAO)
                        values(?, ?, ?) RETURNING ID_LIVRO """, (nome, autor, ano_publicacao))

        id_livro = cursor.fetchone() [0]
        con.commit()

        arquivo = request.files['imagem']
        arquivo.save(f'uploads/capa{id_livro}.jpg')

        flash('Livro criado com sucesso')


    except Exception as e:
        flash(f'Ocorreu um erro -> {e}')
        con.rollback()

    finally:
        cursor.close()
    return redirect(url_for('acervo'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()
    try:
        cursor.execute(""" SELECT id_livro, nome, autor, ano_publicacao FROM livros WHERE id_livro = ? """, (id,))
        livro = cursor.fetchone() #pega um dado só, o id

        if not livro:
            flash('Livro não encontrado')
            return redirect(url_for('acervo'))

        if request.method == 'POST':
            nome = request.form['nome']
            autor = request.form['autor']
            ano_publicacao = request.form['ano_publicacao']

            cursor.execute(""" UPDATE LIVROS SET nome = ?, AUTOR = ?, ANO_PUBLICACAO = ? 
                                WHERE ID_LIVRO = ? """, (nome, autor, ano_publicacao, id))
            con.commit()
            flash('Livro editado com sucesso')
            return redirect(url_for('acervo'))
        return render_template('editar.html', livro=livro)
    except Exception as e:
        con.rollback()
        flash(f'Ocorreu um erro -> {e}')
        return redirect(url_for('acervo'))
    finally:
        cursor.close()


@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    cursor = con.cursor()
    try:
        cursor.execute(""" DELETE FROM livros WHERE id_livro = ? """, (id,))
        con.commit()
        flash('Livro deletado com sucesso')
        return redirect(url_for('acervo'))
    except Exception as e:
        con.rollback()
        flash(f'Ocorreu um erro -> {e}')
        return redirect(url_for('acervo'))
    finally:
        cursor.close()


#tabela usuarios

@app.route("/usuario")
def usuarios():
    cursor = con.cursor() #abrir o cursor

    cursor.execute("""SELECT u.id_usuario, u.nome, u.email, u.senha FROM USUARIOS u 
                        ORDER BY u.NOME """)
    usuarios = cursor.fetchall() #fetchall pega tds os dados da tabela e insere na lista livros

    cursor.close() #fecha o cursor

    return render_template('usuarios.html', usuarios=usuarios)

@app.route("/novo_usuario")
def novo_usuario():
    return render_template('novo_usuario.html')

@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    print('entreu')
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()

    try:
        cursor.execute(""" SELECT 1 FROM USUARIOS u WHERE nome = ? """, (nome,))
        if cursor.fetchone():
            flash('Erro: usuário já cadastrado')
            return redirect(url_for('novo_usuario'))
        cursor.execute("""INSERT INTO USUARIOS (nome, email, senha)
                            VALUES (?, ?, ?)""", (nome, email, senha))
        con.commit()
        flash('Usuário cadastrado com sucesso')


    except Exception as e:
        flash(f'Ocorreu um erro -> {e}')
        con.rollback()

    finally:
        cursor.close()
    return redirect(url_for('usuarios'))

@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    cursor = con.cursor()
    try:
        cursor.execute(""" SELECT id_usuario, nome, email, senha FROM USUARIOS u WHERE ID_USUARIO = ?
                         """, (id,))
        usuarios = cursor.fetchone() #pega um dado só, o id

        if not usuarios:
            flash('Usuário não encontrado')
            return redirect(url_for('usuarios'))

        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']

            cursor.execute(""" UPDATE USUARIOS SET nome = ?, email = ?, senha = ? 
                                WHERE ID_USUARIO = ? """, (nome, email, senha, id))
            con.commit()
            flash('Livro editado com sucesso')
            return redirect(url_for('acervo'))
        return render_template('editar_usuario.html', usuarios = usuarios)
    except Exception as e:
        con.rollback()
        flash(f'Ocorreu um erro -> {e}')
        return redirect(url_for('usuarios'))
    finally:
        cursor.close()

@app.route('/deletar_usuario/<int:id>', methods=['POST'])
def deletar_usuario(id):
    cursor = con.cursor()
    try:
        cursor.execute(""" DELETE FROM usuarios WHERE id_usuario = ? """, (id,))
        con.commit()
        flash('Usuário deletado com sucesso')
        return redirect(url_for('usuarios'))
    except Exception as e:
        con.rollback()
        flash(f'Ocorreu um erro -> {e}')
        return redirect(url_for('usuarios'))
    finally:
        cursor.close()


@app.route("/login")
def login():
   return render_template('login.html')

@app.route('/entrar_usuario', methods=['POST'])
def entrar_usuario():
   email = request.form['email']
   senha = request.form['senha']

   cursor = con.cursor()

   try:
       cursor.execute(""" SELECT id_usuario, senha FROM usuarios
           WHERE email = ? """, (email,))

       usuario = cursor.fetchone()

       if not usuario:
           flash('Usuário não encontrado', 'error')
           return redirect(url_for('login'))

       id_usuario, senha_hash = usuario

       if usuario:
           if bcrypt.check_password_hash(senha_hash, senha):
                session['id_usuario'] = id_usuario

                flash('Login realizado com sucesso!')
                return redirect(url_for('acervo'))
           else:
                flash('Email ou senha incorretos!', 'erro')
                return redirect(url_for('login'))

   except Exception as e:
       flash(f'Ocorreu um erro: {e}')
       return redirect(url_for('login'))

   finally:
       cursor.close()


@app.route("/cadastro", methods=['GET'])
def cadastro():
   return render_template('cadastro.html')

@app.route("/cadastro", methods=['POST'])
def cadastrar_usuario():
   nome = request.form['nome']
   email = request.form['email']
   senha = request.form['senha']

   if not senha_forte(senha):
       flash('Senha fraca! Use pelo menos 8 caracteres, uma maiúscula, uma minúscula e um número.')
       return redirect(url_for('cadastro'))

   cursor = con.cursor()

   try:
       # Verifica se o email já está cadastrado
       cursor.execute(""" SELECT 1 FROM usuarios
           WHERE email = ? """, (email,))

       if cursor.fetchone():
           flash('Erro: email já utilizado')
           return redirect(url_for('cadastro'))

       senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

       # Cadastra o usuário
       cursor.execute(""" INSERT INTO usuarios (nome, email, senha)
           VALUES (?, ?, ?) """, (nome, email, senha_hash))

       con.commit()
       flash('Cadastro realizado com sucesso!')

   except Exception as e:
       flash(f'Ocorreu um erro -> {e}')
       con.rollback()

   finally:
       cursor.close()

   return redirect(url_for('login'))

@app.route("/logout")
def logout():
    session.pop('id_usuario', None)
    flash('Logout realizado com sucesso')
    return redirect(url_for('login'))

@app.route('/livros/relatorio', methods=['GET'])
def relatorio():

    cursor = con.cursor()

    cursor.execute("""
        SELECT id_livro, nome, autor, ano_publicacao
        FROM livros
    """)

    livros = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatório de Livros", ln=True, align='C')

    pdf.ln(5)  # Espaço entre o título e a linha
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha abaixo do título
    pdf.ln(5)  # Espaço após a linha

    pdf.set_font("Arial", size=12)

    for livro in livros:
        pdf.cell(
            200,
            10,
            f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}",
            ln=True
        )

    contador_livros = len(livros)

    pdf.ln(10)  # Espaço antes do contador

    pdf.set_font("Arial", style='B', size=12)

    pdf.cell(
        200,
        10,
        f"Total de livros cadastrados: {contador_livros}",
        ln=True,
        align='C'
    )

    pdf_path = "relatorio_livros.pdf"

    pdf.output(pdf_path)

    return send_file(
        pdf_path,
        as_attachment=True,
        mimetype='application/pdf'
    )


if __name__ == "__main__":
    app.run(debug=True)