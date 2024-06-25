from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import uuid

app = Flask(__name__)
app.secret_key = "quitandazezinho"

# Defining a placeholder user for demonstration purposes
usuario = "Zezé Perrella"
senha = "1234"
login = False

# FUNÇÃO PARA VERIFICAR SESSÃO
def verifica_sessao():
    return session.get("login", False)

def conecta_database():
    conexao = sql.connect("db_quitanda.db")
    conexao.row_factory = sql.Row
    return conexao

# INICIAR O BANCO DE DADOS
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
        conexao.commit()
        conexao.close()

# ROTA DA PÁGINA INICIAL
@app.route("/")
def index():
    iniciar_db()
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
    conexao.close()
    title = "Home"
    return render_template("Home.html", produtos=produtos, title=title)

# ROTA DA PÁGINA LOGIN
@app.route("/login")
def login_page():
    title = "Login"
    return render_template("login.html", title=title)

#ROTA PARA VERIFICAR O ACESSO O ADMIN
@app.route("/acesso", methods=['POST'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]


    if usuario == usuario_informado and senha == senha_informada:
        session["login"] = True
        return redirect('/adm') #homepage
    else:
        return render_template("login.html",msg="Usuário/Senha estão errados!")
   


@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()  # Fix: Call the function to get the connection
        produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
        conexao.close()
        title = "Administração"
        return render_template("adm.html", produtos=produtos, title=title)
    else:
        return redirect("/login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

@app.route("/cadprodutos")
def cadprodutos():
    if verifica_sessao():
        title = "Cadastro de produtos"
        return render_template("cadastro.html", title=title)
    else:
        return redirect("/login")

@app.route("/cadastro", methods=["POST"])
def cadastro():
    if verifica_sessao():
        nome_prod = request.form['nome_prod']
        desc_prod = request.form['desc_prod']
        preco_prod = request.form['preco_prod']
        img_prod = request.files['img_prod']
        id_foto = str(uuid.uuid4().hex)
        filename = id_foto + nome_prod + '.png'
        img_prod.save("static/img/produtos/" + filename)
        conexao = conecta_database()
        conexao.execute('INSERT INTO produtos (nome_prod, desc_prod, preco_prod, img_prod) VALUES (?, ?, ?, ?)',
                        (nome_prod, desc_prod, preco_prod, filename))
        conexao.commit()
        conexao.close()
        return redirect("/adm")
    else:
        return redirect("/login")

@app.route("/excluir/<id>")
def excluir(id):
    if verifica_sessao():
        id = int(id)
        conexao = conecta_database()
        conexao.execute('DELETE FROM produtos WHERE id_prod = ?', (id,))
        conexao.commit()
        conexao.close()
        return redirect('/adm')
    else:
        return redirect("/login")

@app.route("/editprodutos/<id_prod>")
def editar(id_prod):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos WHERE id_prod = ?', (id_prod,)).fetchall()
        conexao.close()
        title = "Edição de Produtos"
        return render_template("editprodutos.html", produtos=produtos, title=title)
    else:
        return redirect("/login")

@app.route("/editarprodutos", methods=['POST'])
def editprod():
    id_prod = request.form['id_prod']
    nome_prod = request.form['nome_prod']
    desc_prod = request.form['desc_prod']
    preco_prod = request.form['preco_prod']
    img_prod = request.files['img_prod']
    id_foto = str(uuid.uuid4().hex)
    filename = id_foto + nome_prod + '.png'
    img_prod.save("static/img/produtos/" + filename)
    conexao = conecta_database()
    conexao.execute(
        'UPDATE produtos SET nome_prod = ?, desc_prod = ?, preco_prod = ?, img_prod = ? WHERE id_prod = ?',
        (nome_prod, desc_prod, preco_prod, filename, id_prod))
    conexao.commit()
    conexao.close()
    return redirect('/adm')

@app.route("/busca", methods=["POST"])
def busca():
    busca = request.form['buscar']
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos WHERE nome_prod LIKE "%" || ? || "%"', (busca,)).fetchall()
    title = "Home"
    return render_template("home.html", produtos=produtos, title=title)

@app.route("/quem")
def quem():
    return render_template ("quem_somos.html")


app.run(debug=True)
