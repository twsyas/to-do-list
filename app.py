from flask import Flask, render_template, url_for, flash, get_flashed_messages, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import date, time

app = Flask(__name__, template_folder= "templates") # template_folder muda o local da pasta templates. tira o default. modificavel.
# Endereço do banco
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
login_manager = LoginManager(app) # gerencia o login
db = SQLAlchemy(app) # gerencia o banco de dados
# Gerando uma chave secreta, para ser nossa chave de sessão do usuário
app.config['SECRET_KEY'] =  secrets.token_hex(16) # 'app.config' é um dicionário (para ver é só printar). o "token_hex" gera uma chave caractere.
app.app_context().push() # cria o contexto do banco de dados no app

@login_manager.user_loader #retorna o usuario atual
def current_user(user_id):
    return Usuario.query.get(user_id)

class Usuario(db.Model, UserMixin): # Criando uma tabela para os dados do usuário. "db.Model" adiciona tudo em coluna. "UserMixin" : tratar de usuário e senha
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.String(84), nullable = False)
    email = db.Column(db.String(84), nullable = False, unique = True)
    senha = db.Column(db.String(84), nullable = False)

class Tarefas(db.Model): # classe das tarefas da todolist
    __tablename__ = 'tarefas' 
    id_tarefa = db.Column(db.Integer, primary_key = True)
    titulo = db.Column(db.String(84), nullable = False)
    hora = db.Column(db.String(84), nullable = False)
    prazo = db.Column(db.String(84), nullable = False)
    prioridade = db.Column(db.String(84), nullable = False)

#db.create_all() # cria banco de dados

#### CADASTRO ####

@app.route("/cadastro", methods = ['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        usuario = Usuario()
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        usuario.senha = generate_password_hash(request.form['senha'])

        db.session.add(usuario) # adiciona no banco de dados
        db.session.commit() # permanecer no banco de dados
        return redirect(url_for('login'))
    return render_template('cadastro.html')

#### LOGIN ####


@app.route("/", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario:
            flash('Usuário não encontrado!')
            return redirect(url_for('cadastro'))
        elif not check_password_hash(usuario.senha, senha):
            flash('Senha incorreta!')
            return redirect(url_for('login'))
        else:
            flash('Usuário logado!')
            login_user(usuario)
            return redirect(url_for('tarefas'))
    return render_template('login.html')

#### TAREFAS ####

@app.route("/tarefas", methods=['GET','POST'])
@login_required 
def tarefas():
    if request.method == 'POST':
        tarefa = Tarefas()
        tarefa.titulo = request.form['titulo']
        tarefa.hora = request.form['hora']
        tarefa.prazo = request.form['prazo']
        tarefa.prioridade = request.form['prioridade']

        db.session.add(tarefa) # adiciona no banco de dados
        db.session.commit() # permanecer no banco de dados
        flash("Tarefa cadastrada")
        return redirect(url_for('tarefas'))
    tarefas = Tarefas.query.all() # consulta no banco
    #agora = datetime.time.now
    return render_template('tarefas.html', tarefas=tarefas)

#### LOGOUT ####
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

#### DELETAR TAREFA ####
@app.route("/deletar/<int:id>")
@login_required
def deletar_tarefa(id):
    tarefa = Tarefas.query.filter_by(id_tarefa=id).first()
    db.session.delete(tarefa)
    db.session.commit()
    return redirect(url_for('tarefas'))


if __name__ == "__main__":
    app.run(debug = True) 