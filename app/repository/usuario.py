from decouple import config
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.exceptions import HTTPException
from fastapi import status
from schemas.usuario import Usuarios, TokenData
from db.models import Usuarios as UsuariosModel

# jose -> assinatura e criptografia de objs JSON 
# jwt -> algoritmo do tipo JWT p signin

# Instanciando o CryptContext -> Usa qual contexto da senha? usa o schema sha256_crypt
crypt_context = CryptContext(schemes=['sha256_crypt'])
SECRET_KEY = "  "  ##gerar a chave 
ALGORITHM = "HS256"

# classe Usuarios da repository
class UsuariosRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    # Método Salvar usuário
    @staticmethod # serve pra não precisar instanciar as classes
    def save_user(db: Session, user: Usuarios):
        user_on_db = UsuariosModel(
            username=user.username,
            password=crypt_context.hash(user.password) # cryptografa a senha do user
        )
        db.add(user_on_db)

        try:
            db.commit() # -> confirma
        except IntegrityError:
            db.rollback() # -> cancela se tiver prob de integridade de dados
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exists')
    
    # Método Login usuário
    def user_login(self, user: Usuarios, expires_in: int = 30): # def tempo de duração da token
        user_on_db = self._get_user(username=user.username)
    
        # Verifica se usuário ou senha não existem no db
        if user_on_db is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Username or password does not exist')

        # Verifica se senha criptografada existe ou não
        if not crypt_context.verify(user.password, user_on_db.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Username or password does not exist')
        
        expires_at = datetime.utcnow() + timedelta(expires_in)

        data = {
            'sub': user_on_db.username,
            'exp': expires_at
        }

        access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

        token_data = TokenData(access_token=access_token, expires_at=expires_at)
        return token_data

    
    # Método Verificação de Token
    def verify_token(self, token: str):
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
        
        user_on_db = self._get_user(username=data['sub'])

        if user_on_db is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    # Método Filtrar por Nome
    def find_by_name(self, username: str):
        user_on_db = self.query(UsuariosModel).filter_by(username=username).first()
        return user_on_db
    
    # Método Escolher usuário
    def _get_user(self, username: str):
        user_on_db = self.db_session.query(UsuariosModel).filter_by(username=username).first()
        return user_on_db

    # Método usuário já existe no db
    @staticmethod
    def exists_by_id_user(db:Session, id: int) -> bool:
        return db.query(UsuariosModel).filter(UsuariosModel.id ==id).first()

    @staticmethod
    def delete_user_by_id(db: Session,id: int) -> None:
        usuario = db.query(UsuariosModel).filter(UsuariosModel.id == id).first()
        if usuario is not None:
            db.delete(usuario)
            db.commit()
            return "Usuário excluído"
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )

# Token = header + payload + signature
# Token = cabeçalho + carga útil + assinatura (chave secreta)

#   header -> algoritmo e tipo de token { alg: RS256, type: JWT}
#   payload -> dados {sub:12345678, name: john , admin: true }
#   verify signature -> assinatura RSASHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)

#codificar e decodificar

#jwt.io -> site para testar codificações