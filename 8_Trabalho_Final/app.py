import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from models import db, Parecer, Prazo, Usuario, StatusFormulario, Perfil
from datetime import datetime, date, time
from sqlalchemy import inspect, text

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf'}

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Você precisa estar autenticado para acessar esta página.'
login_manager.login_message_category = 'error'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def seed_data():
    if db.session.query(Perfil).count() == 0:
        perfis = [
            Perfil(nome='Administrativo'),
            Perfil(nome='Parecerista'),
            Perfil(nome='Admin'),
        ]
        db.session.add_all(perfis)
        db.session.commit()
    
    if db.session.query(Prazo).count() == 0:
        prazos = [
            Prazo(nome='5 dias'),
            Prazo(nome='10 dias'),
            Prazo(nome='15 dias'),
            Prazo(nome='30 dias'),
            Prazo(nome='60 dias'),
        ]
        db.session.add_all(prazos)
    
    if db.session.query(Usuario).count() == 0:
        perfil_admin = db.session.query(Perfil).filter_by(nome='Admin').first()
        perfil_administrativo = db.session.query(Perfil).filter_by(nome='Administrativo').first()
        perfil_parecerista = db.session.query(Perfil).filter_by(nome='Parecerista').first()
        
        usuarios = [
            Usuario(nome='Admin Sistema', email='admin@example.com', senha_hash=generate_password_hash('senha123'), perfil_id=perfil_admin.id),
            Usuario(nome='João Silva', email='joao.silva@example.com', senha_hash=generate_password_hash('senha123'), perfil_id=perfil_administrativo.id),
            Usuario(nome='Maria Santos', email='maria.santos@example.com', senha_hash=generate_password_hash('senha123'), perfil_id=perfil_parecerista.id),
            Usuario(nome='Pedro Oliveira', email='pedro.oliveira@example.com', senha_hash=generate_password_hash('senha123'), perfil_id=perfil_administrativo.id),
        ]
        db.session.add_all(usuarios)
    
    db.session.commit()


def migrate_id_elaborador():
    """Verifica e cria a coluna id_elaborador na tabela pareceres se não existir."""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('pareceres')]
    
    if 'id_elaborador' not in columns:
        print("Coluna id_elaborador não encontrada. Criando...")
        try:
            with db.engine.begin() as connection:
                connection.execute(text(
                    "ALTER TABLE pareceres ADD COLUMN id_elaborador INTEGER NULL"
                ))
                connection.execute(text(
                    "ALTER TABLE pareceres ADD CONSTRAINT fk_pareceres_id_elaborador_usuarios "
                    "FOREIGN KEY (id_elaborador) REFERENCES usuarios(id) ON DELETE SET NULL"
                ))
                connection.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_pareceres_id_elaborador ON pareceres(id_elaborador)"
                ))
            print("Coluna id_elaborador criada com sucesso!")
        except Exception as e:
            print(f"Erro ao criar coluna id_elaborador: {e}")
    else:
        print("Coluna id_elaborador já existe.")


with app.app_context():
    db.create_all()
    migrate_id_elaborador()
    seed_data()


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def can_create_parecer_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.can_create_parecer():
            flash('Acesso negado. Você não tem permissão para criar pareceres.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        
        if not email or not senha:
            flash('Email e senha são obrigatórios.', 'error')
            return render_template('login.html')
        
        usuario = db.session.query(Usuario).filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.senha_hash, senha):
            login_user(usuario)
            flash(f'Bem-vindo, {usuario.nome}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    perfis = db.session.query(Perfil).all()
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        senha_confirm = request.form.get('senha_confirm', '')
        perfil_id = request.form.get('perfil_id', '')
        
        if not nome or not email or not senha or not senha_confirm or not perfil_id:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('register.html', perfis=perfis)
        
        if senha != senha_confirm:
            flash('As senhas não coincidem.', 'error')
            return render_template('register.html', perfis=perfis)
        
        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('register.html', perfis=perfis)
        
        usuario_existente = db.session.query(Usuario).filter_by(email=email).first()
        if usuario_existente:
            flash('Este email já está cadastrado.', 'error')
            return render_template('register.html', perfis=perfis)
        
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),
            perfil_id=int(perfil_id)
        )
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', perfis=perfis)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    if not (current_user.is_admin() or current_user.is_administrativo()):
        flash('Acesso negado. Apenas administradores e administrativos podem acessar o Painel Geral.', 'error')
        abort(403)
    
    search = request.args.get('search', '')
    status_filter = request.args.get('status_filter', '')
    sort_by = request.args.get('sort_by', 'dt_recebimento')
    sort_order = request.args.get('sort_order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = db.session.query(Parecer)
    
    if search:
        query = query.filter(Parecer.n_processo.ilike(f'%{search}%'))
    
    if status_filter:
        try:
            status_enum = StatusFormulario[status_filter]
            query = query.filter(Parecer.status_formulario == status_enum)
        except KeyError:
            pass
    
    if sort_by == 'n_processo':
        column = Parecer.n_processo
    elif sort_by == 'dt_recebimento':
        column = Parecer.dt_recebimento
    elif sort_by == 'status':
        column = Parecer.status_formulario
    else:
        column = Parecer.dt_recebimento
    
    if sort_order == 'asc':
        query = query.order_by(column.asc().nullslast())
    else:
        query = query.order_by(column.desc().nullslast())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    pareceres = pagination.items
    
    prazos = db.session.query(Prazo).all()
    usuarios = db.session.query(Usuario).all()
    
    return render_template('painel_geral.html', 
                         pareceres=pareceres,
                         pagination=pagination,
                         prazos=prazos,
                         usuarios=usuarios,
                         search=search,
                         status_filter=status_filter,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         StatusFormulario=StatusFormulario)


@app.route('/meus-pareceres')
@login_required
def meus_pareceres():
    if not (current_user.is_admin() or current_user.is_parecerista()):
        flash('Acesso negado. Apenas pareceristas e administradores podem acessar este painel.', 'error')
        abort(403)
    
    search = request.args.get('search', '')
    status_filter = request.args.get('status_filter', '')
    sort_by = request.args.get('sort_by', 'dt_recebimento')
    sort_order = request.args.get('sort_order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = db.session.query(Parecer).filter(
        Parecer.status_formulario.in_([StatusFormulario.ELABORACAO, StatusFormulario.REVISAO])
    )
    
    if search:
        query = query.filter(Parecer.n_processo.ilike(f'%{search}%'))
    
    if status_filter:
        try:
            status_enum = StatusFormulario[status_filter]
            query = query.filter(Parecer.status_formulario == status_enum)
        except KeyError:
            pass
    
    if sort_by == 'n_processo':
        column = Parecer.n_processo
    elif sort_by == 'dt_recebimento':
        column = Parecer.dt_recebimento
    elif sort_by == 'status':
        column = Parecer.status_formulario
    else:
        column = Parecer.dt_recebimento
    
    if sort_order == 'asc':
        query = query.order_by(column.asc().nullslast())
    else:
        query = query.order_by(column.desc().nullslast())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    pareceres = pagination.items
    
    prazos = db.session.query(Prazo).all()
    usuarios = db.session.query(Usuario).all()
    
    return render_template('painel_parecerista.html', 
                         pareceres=pareceres,
                         pagination=pagination,
                         prazos=prazos,
                         usuarios=usuarios,
                         search=search,
                         status_filter=status_filter,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         StatusFormulario=StatusFormulario)


@app.route('/historico')
@login_required
def historico():
    search = request.args.get('search', '')
    status_filter = request.args.get('status_filter', '')
    parecerista_filter = request.args.get('parecerista_filter', '')
    dt_inicio = request.args.get('dt_inicio', '')
    dt_fim = request.args.get('dt_fim', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = db.session.query(Parecer).order_by(
        Parecer.updated_at.desc().nullslast(),
        Parecer.id.desc()
    )
    
    if search:
        query = query.filter(Parecer.n_processo.ilike(f'%{search}%'))
    
    if status_filter:
        try:
            status_enum = StatusFormulario[status_filter]
            query = query.filter(Parecer.status_formulario == status_enum)
        except KeyError:
            pass
    
    if parecerista_filter:
        try:
            parecerista_id = int(parecerista_filter)
            query = query.filter(
                (Parecer.id_revisor == parecerista_id)
            )
        except ValueError:
            pass
    
    if dt_inicio:
        try:
            data_inicio = datetime.strptime(dt_inicio, '%Y-%m-%d').date()
            query = query.filter(Parecer.dt_recebimento >= data_inicio)
        except ValueError:
            pass
    
    if dt_fim:
        try:
            data_fim = datetime.strptime(dt_fim, '%Y-%m-%d').date()
            query = query.filter(Parecer.dt_recebimento <= data_fim)
        except ValueError:
            pass
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    pareceres = pagination.items
    
    usuarios = db.session.query(Usuario).all()
    
    return render_template('historico.html', 
                         pareceres=pareceres,
                         pagination=pagination,
                         usuarios=usuarios,
                         search=search,
                         status_filter=status_filter,
                         parecerista_filter=parecerista_filter,
                         dt_inicio=dt_inicio,
                         dt_fim=dt_fim,
                         StatusFormulario=StatusFormulario)


@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin() or current_user.is_administrativo():
            return redirect(url_for('dashboard'))
        elif current_user.is_parecerista():
            return redirect(url_for('meus_pareceres'))
        else:
            return redirect(url_for('historico'))
    else:
        return redirect(url_for('login'))


@app.route('/parecer/novo', methods=['GET', 'POST'])
@login_required
@can_create_parecer_required
def novo_parecer():
    if request.method == 'POST':
        parecer = Parecer(status_formulario=StatusFormulario.INICIADO)
        db.session.add(parecer)
        db.session.commit()
        flash('Parecer criado com sucesso!', 'success')
        return redirect(url_for('editar_parecer', parecer_id=parecer.id))
    
    return redirect(url_for('editar_parecer', parecer_id=0))


@app.route('/parecer/<int:parecer_id>')
def visualizar_parecer(parecer_id):
    parecer = db.get_or_404(Parecer, parecer_id)
    prazos = db.session.query(Prazo).all()
    usuarios = db.session.query(Usuario).all()
    
    can_edit = current_user.is_authenticated and current_user.can_edit_stage(parecer.status_formulario)
    can_advance = current_user.is_authenticated and (current_user.is_admin() or current_user.can_edit_stage(parecer.status_formulario))
    can_delete = current_user.is_authenticated and current_user.is_admin()
    
    return render_template('visualizar.html', 
                         parecer=parecer,
                         prazos=prazos,
                         usuarios=usuarios,
                         StatusFormulario=StatusFormulario,
                         can_edit=can_edit,
                         can_advance=can_advance,
                         can_delete=can_delete)


@app.route('/parecer/<int:parecer_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_parecer(parecer_id):
    if parecer_id == 0:
        parecer = Parecer(status_formulario=StatusFormulario.INICIADO)
        db.session.add(parecer)
        db.session.commit()
        return redirect(url_for('editar_parecer', parecer_id=parecer.id))
    
    parecer = db.get_or_404(Parecer, parecer_id)
    
    if request.method == 'POST':
        if not current_user.can_edit_stage(parecer.status_formulario):
            flash('Você não tem permissão para editar pareceres neste estágio.', 'error')
            abort(403)
        parecer.n_processo = request.form.get('n_processo', '').strip() or None
        parecer.interessado = request.form.get('interessado', '').strip() or None
        parecer.magistrado = request.form.get('magistrado', '').strip() or None
        parecer.comarca = request.form.get('comarca', '').strip() or None
        parecer.serventia = request.form.get('serventia', '').strip() or None
        
        if request.form.get('dt_despacho'):
            parecer.dt_despacho = datetime.strptime(request.form.get('dt_despacho'), '%Y-%m-%d').date()
        
        if request.form.get('dt_encaminhamento'):
            parecer.dt_encaminhamento = datetime.strptime(request.form.get('dt_encaminhamento'), '%Y-%m-%d').date()
        
        if request.form.get('hr_encaminhamento'):
            parecer.hr_encaminhamento = datetime.strptime(request.form.get('hr_encaminhamento'), '%H:%M').time()
        
        if request.form.get('dt_recebimento'):
            parecer.dt_recebimento = datetime.strptime(request.form.get('dt_recebimento'), '%Y-%m-%d').date()
        
        if request.form.get('hr_recebimento'):
            parecer.hr_recebimento = datetime.strptime(request.form.get('hr_recebimento'), '%H:%M').time()
        
        if request.form.get('id_prazo'):
            parecer.id_prazo = int(request.form.get('id_prazo'))
        
        if request.form.get('qt_objetos'):
            parecer.qt_objetos = int(request.form.get('qt_objetos'))
        
        parecer.nota_tecnica = request.form.get('nota_tecnica', '').strip() or None
        
        if parecer.status_formulario == StatusFormulario.ELABORACAO and not parecer.id_elaborador:
            parecer.id_elaborador = current_user.id
        
        if 'nota_tecnica_pdf' in request.files:
            file = request.files['nota_tecnica_pdf']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"nota_tecnica_{parecer.id}_{timestamp}_{filename}"
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                parecer.nota_tecnica_pdf = filename
                flash('PDF da Nota Técnica anexado com sucesso!', 'success')
            elif file and file.filename and not allowed_file(file.filename):
                flash('Apenas arquivos PDF são permitidos.', 'error')
        
        if request.form.get('id_revisor'):
            parecer.id_revisor = int(request.form.get('id_revisor'))
        
        if request.form.get('dt_revisao'):
            parecer.dt_revisao = datetime.strptime(request.form.get('dt_revisao'), '%Y-%m-%d').date()
        
        if request.form.get('hr_revisao'):
            parecer.hr_revisao = datetime.strptime(request.form.get('hr_revisao'), '%H:%M').time()
        
        if request.form.get('id_responsavel_envio'):
            parecer.id_responsavel_envio = int(request.form.get('id_responsavel_envio'))
        
        if request.form.get('dt_envio'):
            parecer.dt_envio = datetime.strptime(request.form.get('dt_envio'), '%Y-%m-%d').date()
        
        if request.form.get('hr_envio'):
            parecer.hr_envio = datetime.strptime(request.form.get('hr_envio'), '%H:%M').time()
        
        parecer.forma_envio = request.form.get('forma_envio', '').strip() or None
        parecer.forma_envio_email = request.form.get('forma_envio_email', '').strip() or None
        
        db.session.commit()
        flash('Parecer salvo com sucesso!', 'success')
        return redirect(url_for('editar_parecer', parecer_id=parecer.id))
    
    prazos = db.session.query(Prazo).all()
    usuarios = db.session.query(Usuario).all()
    
    user_permissions = {
        'can_edit_iniciado': current_user.can_edit_stage(StatusFormulario.INICIADO),
        'can_edit_elaboracao': current_user.can_edit_stage(StatusFormulario.ELABORACAO),
        'can_edit_revisao': current_user.can_edit_stage(StatusFormulario.REVISAO),
        'can_edit_pronto_envio': current_user.can_edit_stage(StatusFormulario.PRONTO_ENVIO),
    }
    
    return render_template('editar.html', 
                         parecer=parecer,
                         prazos=prazos,
                         usuarios=usuarios,
                         StatusFormulario=StatusFormulario,
                         user_permissions=user_permissions)


@app.route('/parecer/<int:parecer_id>/avancar', methods=['POST'])
@login_required
def avancar_parecer(parecer_id):
    parecer = db.get_or_404(Parecer, parecer_id)
    
    if not current_user.can_advance_stage(parecer.status_formulario):
        flash('Você não tem permissão para avançar pareceres neste estágio.', 'error')
        abort(403)
    
    if not parecer.can_advance():
        flash('Não é possível avançar este parecer.', 'error')
        return redirect(url_for('visualizar_parecer', parecer_id=parecer.id))
    
    next_stage = parecer.get_next_stage()
    errors = parecer.validate_for_stage(next_stage)
    
    if errors:
        flash('Não é possível avançar. Campos obrigatórios faltando: ' + ', '.join(errors), 'error')
        return redirect(url_for('editar_parecer', parecer_id=parecer.id))
    
    parecer.status_formulario = next_stage
    db.session.commit()
    flash(f'Parecer avançado para "{Parecer.STAGE_LABELS[next_stage]}"!', 'success')
    return redirect(url_for('visualizar_parecer', parecer_id=parecer.id))


@app.route('/parecer/<int:parecer_id>/voltar', methods=['POST'])
@login_required
def voltar_parecer(parecer_id):
    parecer = db.get_or_404(Parecer, parecer_id)
    
    previous_stage = parecer.get_previous_stage()
    
    if not current_user.can_advance_stage(previous_stage):
        flash('Você não tem permissão para voltar pareceres para este estágio.', 'error')
        abort(403)
    
    if not parecer.can_go_back():
        flash('Não é possível voltar este parecer.', 'error')
        return redirect(url_for('visualizar_parecer', parecer_id=parecer.id))
    
    parecer.status_formulario = previous_stage
    db.session.commit()
    flash(f'Parecer retornado para "{Parecer.STAGE_LABELS[previous_stage]}"!', 'success')
    return redirect(url_for('visualizar_parecer', parecer_id=parecer.id))


@app.route('/parecer/<int:parecer_id>/excluir', methods=['POST'])
@login_required
def excluir_parecer(parecer_id):
    if not current_user.is_admin():
        flash('Apenas administradores podem excluir pareceres.', 'error')
        abort(403)
    
    parecer = db.get_or_404(Parecer, parecer_id)
    db.session.delete(parecer)
    db.session.commit()
    flash('Parecer excluído com sucesso!', 'success')
    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/parecer/<int:parecer_id>/download-pdf')
@login_required
def download_pdf(parecer_id):
    parecer = db.get_or_404(Parecer, parecer_id)
    
    if not parecer.nota_tecnica_pdf:
        flash('Este parecer não possui PDF anexado.', 'error')
        abort(404)
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], parecer.nota_tecnica_pdf)


@app.route('/usuarios')
@login_required
@admin_required
def usuarios():
    usuarios = db.session.query(Usuario).all()
    return render_template('usuarios.html', usuarios=usuarios)


@app.route('/usuario/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_usuario():
    perfis = db.session.query(Perfil).all()
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        perfil_id = request.form.get('perfil_id', '')
        
        if not nome or not email or not senha or not perfil_id:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('usuario_form.html', perfis=perfis, usuario=None)
        
        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('usuario_form.html', perfis=perfis, usuario=None)
        
        usuario_existente = db.session.query(Usuario).filter_by(email=email).first()
        if usuario_existente:
            flash('Este email já está cadastrado.', 'error')
            return render_template('usuario_form.html', perfis=perfis, usuario=None)
        
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),
            perfil_id=int(perfil_id)
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('usuarios'))
    
    return render_template('usuario_form.html', perfis=perfis, usuario=None)


@app.route('/usuario/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    perfis = db.session.query(Perfil).all()
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        perfil_id = request.form.get('perfil_id', '')
        
        if not nome or not email or not perfil_id:
            flash('Nome, email e perfil são obrigatórios.', 'error')
            return render_template('usuario_form.html', perfis=perfis, usuario=usuario)
        
        if senha and len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('usuario_form.html', perfis=perfis, usuario=usuario)
        
        if email != usuario.email:
            usuario_existente = db.session.query(Usuario).filter_by(email=email).first()
            if usuario_existente:
                flash('Este email já está cadastrado.', 'error')
                return render_template('usuario_form.html', perfis=perfis, usuario=usuario)
        
        usuario.nome = nome
        usuario.email = email
        usuario.perfil_id = int(perfil_id)
        
        if senha:
            usuario.senha_hash = generate_password_hash(senha)
        
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('usuarios'))
    
    return render_template('usuario_form.html', perfis=perfis, usuario=usuario)


@app.route('/usuario/<int:usuario_id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_usuario(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    
    if usuario.id == current_user.id:
        flash('Você não pode excluir sua própria conta.', 'error')
        return redirect(url_for('usuarios'))
    
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('usuarios'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
