from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import UserMixin
import enum


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class StatusFormulario(enum.Enum):
    INICIADO = "INICIADO"
    ELABORACAO = "ELABORACAO"
    REVISAO = "REVISAO"
    PRONTO_ENVIO = "PRONTO_ENVIO"


class Perfil(Base):
    __tablename__ = 'perfis'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False, unique=True)
    
    usuarios = relationship('Usuario', back_populates='perfil')


class Prazo(Base):
    __tablename__ = 'prazos'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    
    pareceres = relationship('Parecer', back_populates='prazo')


class Usuario(UserMixin, Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    perfil_id = Column(Integer, ForeignKey('perfis.id'), nullable=False)
    
    perfil = relationship('Perfil', back_populates='usuarios')
    pareceres_elaborador = relationship('Parecer', foreign_keys='Parecer.id_elaborador', back_populates='elaborador')
    pareceres_revisor = relationship('Parecer', foreign_keys='Parecer.id_revisor', back_populates='revisor')
    pareceres_responsavel = relationship('Parecer', foreign_keys='Parecer.id_responsavel_envio', back_populates='responsavel_envio')
    
    def is_admin(self):
        return self.perfil and self.perfil.nome == 'Admin'
    
    def is_administrativo(self):
        return self.perfil and self.perfil.nome == 'Administrativo'
    
    def is_parecerista(self):
        return self.perfil and self.perfil.nome == 'Parecerista'
    
    def can_create_form(self):
        return self.is_admin() or self.is_administrativo()
    
    def can_create_parecer(self):
        return self.can_create_form()
    
    def can_edit_stage(self, status):
        if self.is_admin():
            return True
        
        if status == StatusFormulario.INICIADO:
            return self.is_administrativo()
        elif status == StatusFormulario.ELABORACAO:
            return self.is_parecerista()
        elif status == StatusFormulario.REVISAO:
            return self.is_parecerista()
        elif status == StatusFormulario.PRONTO_ENVIO:
            return self.is_administrativo()
        
        return False
    
    def can_advance_stage(self, status):
        if self.is_admin():
            return True
        
        if status == StatusFormulario.INICIADO:
            return self.is_administrativo()
        elif status == StatusFormulario.ELABORACAO:
            return self.is_parecerista()
        elif status == StatusFormulario.REVISAO:
            return self.is_parecerista()
        elif status == StatusFormulario.PRONTO_ENVIO:
            return self.is_administrativo()
        
        return False
    
    def can_manage_users(self):
        return self.is_admin()


class Parecer(Base):
    __tablename__ = 'pareceres'
    
    id = Column(Integer, primary_key=True)
    status_formulario = Column(SQLEnum(StatusFormulario), nullable=False, default=StatusFormulario.INICIADO)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    n_processo = Column(String(100))
    interessado = Column(String(200))
    magistrado = Column(String(200))
    comarca = Column(String(200))
    serventia = Column(String(200))
    dt_despacho = Column(Date)
    dt_encaminhamento = Column(Date)
    hr_encaminhamento = Column(Time)
    dt_recebimento = Column(Date)
    hr_recebimento = Column(Time)
    
    id_prazo = Column(Integer, ForeignKey('prazos.id'))
    qt_objetos = Column(Integer)
    nota_tecnica = Column(Text)
    nota_tecnica_pdf = Column(String(500))
    
    id_elaborador = Column(Integer, ForeignKey('usuarios.id'))
    id_revisor = Column(Integer, ForeignKey('usuarios.id'))
    dt_revisao = Column(Date)
    hr_revisao = Column(Time)
    
    id_responsavel_envio = Column(Integer, ForeignKey('usuarios.id'))
    dt_envio = Column(Date)
    hr_envio = Column(Time)
    forma_envio = Column(String(100))
    forma_envio_email = Column(String(200))
    
    prazo = relationship('Prazo', back_populates='pareceres')
    elaborador = relationship('Usuario', foreign_keys=[id_elaborador], back_populates='pareceres_elaborador')
    revisor = relationship('Usuario', foreign_keys=[id_revisor], back_populates='pareceres_revisor')
    responsavel_envio = relationship('Usuario', foreign_keys=[id_responsavel_envio], back_populates='pareceres_responsavel')
    
    STAGE_LABELS = {
        StatusFormulario.INICIADO: 'Iniciado',
        StatusFormulario.ELABORACAO: 'Em elaboração',
        StatusFormulario.REVISAO: 'Em revisão',
        StatusFormulario.PRONTO_ENVIO: 'Pronto para envio'
    }
    
    STAGE_ORDER = [
        StatusFormulario.INICIADO,
        StatusFormulario.ELABORACAO,
        StatusFormulario.REVISAO,
        StatusFormulario.PRONTO_ENVIO
    ]
    
    def can_advance(self):
        current_index = self.STAGE_ORDER.index(self.status_formulario)
        return current_index < len(self.STAGE_ORDER) - 1
    
    def can_go_back(self):
        current_index = self.STAGE_ORDER.index(self.status_formulario)
        return current_index > 0
    
    def get_next_stage(self):
        if self.can_advance():
            current_index = self.STAGE_ORDER.index(self.status_formulario)
            return self.STAGE_ORDER[current_index + 1]
        return None
    
    def get_previous_stage(self):
        if self.can_go_back():
            current_index = self.STAGE_ORDER.index(self.status_formulario)
            return self.STAGE_ORDER[current_index - 1]
        return None
    
    def validate_for_stage(self, stage):
        errors = []
        
        if stage == StatusFormulario.INICIADO:
            pass
        
        elif stage == StatusFormulario.ELABORACAO:
            if not self.n_processo:
                errors.append('Nº do Processo é obrigatório')
            if not self.interessado:
                errors.append('Interessado é obrigatório')
            if not self.magistrado:
                errors.append('Magistrado é obrigatório')
            if not self.comarca:
                errors.append('Comarca é obrigatória')
            if not self.serventia:
                errors.append('Serventia é obrigatória')
            if not self.dt_despacho:
                errors.append('Data de Despacho é obrigatória')
            if not self.dt_encaminhamento:
                errors.append('Data de Encaminhamento é obrigatória')
            if not self.hr_encaminhamento:
                errors.append('Hora de Encaminhamento é obrigatória')
            if not self.dt_recebimento:
                errors.append('Data de Recebimento é obrigatória')
            if not self.hr_recebimento:
                errors.append('Hora de Recebimento é obrigatória')
        
        elif stage == StatusFormulario.REVISAO:
            if not self.n_processo:
                errors.append('Nº do Processo é obrigatório')
            if not self.interessado:
                errors.append('Interessado é obrigatório')
            if not self.magistrado:
                errors.append('Magistrado é obrigatório')
            if not self.comarca:
                errors.append('Comarca é obrigatória')
            if not self.serventia:
                errors.append('Serventia é obrigatória')
            if not self.dt_despacho:
                errors.append('Data de Despacho é obrigatória')
            if not self.dt_encaminhamento:
                errors.append('Data de Encaminhamento é obrigatória')
            if not self.hr_encaminhamento:
                errors.append('Hora de Encaminhamento é obrigatória')
            if not self.dt_recebimento:
                errors.append('Data de Recebimento é obrigatória')
            if not self.hr_recebimento:
                errors.append('Hora de Recebimento é obrigatória')
            if not self.id_prazo:
                errors.append('Prazo é obrigatório')

            if self.qt_objetos is None:
                errors.append('Quantidade de Objetos é obrigatória')
            if not self.nota_tecnica:
                errors.append('Nota Técnica é obrigatória')
        
        elif stage == StatusFormulario.PRONTO_ENVIO:
            if not self.n_processo:
                errors.append('Nº do Processo é obrigatório')
            if not self.interessado:
                errors.append('Interessado é obrigatório')
            if not self.magistrado:
                errors.append('Magistrado é obrigatório')
            if not self.comarca:
                errors.append('Comarca é obrigatória')
            if not self.serventia:
                errors.append('Serventia é obrigatória')
            if not self.dt_despacho:
                errors.append('Data de Despacho é obrigatória')
            if not self.dt_encaminhamento:
                errors.append('Data de Encaminhamento é obrigatória')
            if not self.hr_encaminhamento:
                errors.append('Hora de Encaminhamento é obrigatória')
            if not self.dt_recebimento:
                errors.append('Data de Recebimento é obrigatória')
            if not self.hr_recebimento:
                errors.append('Hora de Recebimento é obrigatória')
            if not self.id_prazo:
                errors.append('Prazo é obrigatório')

            if self.qt_objetos is None:
                errors.append('Quantidade de Objetos é obrigatória')
            if not self.nota_tecnica:
                errors.append('Nota Técnica é obrigatória')
            if not self.id_revisor:
                errors.append('Revisor é obrigatório')
            if not self.dt_revisao:
                errors.append('Data de Revisão é obrigatória')
            if not self.hr_revisao:
                errors.append('Hora de Revisão é obrigatória')
        
        return errors
    
    def get_parecerista_elaborador(self):
        return self.elaborador.nome if self.elaborador else 'Não informado'
