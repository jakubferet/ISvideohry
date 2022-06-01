from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, Sequence, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_utils.functions import database_exists, create_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg2
import datetime
import graphene
import uvicorn
from multiprocessing import Process
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#import fastapi
#import requests

#############################
#   POSTGRES CONNECTION     #
#############################

connectionstring = 'postgresql+psycopg2://postgres:example@postgres/videohry'
if not database_exists(connectionstring):  #=> False
    try:
        create_database(connectionstring)
        doCreateAll = True
        print('Database created')
    except Exception as e:
        print('Database does not exists and cannot be created')
        raise
else:
    print('Database already exists')

engine = create_engine(connectionstring)

#####################
#   SQL MODELS      #
#####################

BaseModel = declarative_base()

unitedSequence = Sequence('all_id_seq')

class VyvSpolZanrModel(BaseModel):
    __tablename__ = 'zamereni'
    
    id = Column(BigInteger, Sequence('all_id_seq'), primary_key=True)
    vyvspol_id = Column(ForeignKey('vyvspol.id'))
    vyvspol = relationship('VyvSpolModel', back_populates='zamereni')
    zanr_id = Column(ForeignKey('zanr.id'))
    zanr = relationship('ZanrModel', back_populates='zamereni')

#VyvSpolZanrModel = Table('zamereni', BaseModel.metadata,
#        Column('id', BigInteger, Sequence('all_id_seq'), primary_key=True),
#        Column('vyvspol_id', ForeignKey('vyvspol.id'), primary_key=True),
#        Column('zanr_id', ForeignKey('zanr.id'), primary_key=True)
#)

class VideohraModel(BaseModel):
    __tablename__ = 'videohra'
    
    id = Column(BigInteger, Sequence('all_id_seq'), primary_key=True)
    nazev = Column(String)
    rok = Column(Integer)
    doba = Column(String)
    obtiznost = Column(String)
    
    lastchange = Column(DateTime, default=datetime.datetime.now)
    #externalId = Column(BigInteger, index=True)

    vyvspol_id = Column(ForeignKey('vyvspol.id'))
    vyvspol = relationship('VyvSpolModel', back_populates='videohry')
    
    zanr_id = Column(ForeignKey('zanr.id'))
    zanr = relationship('ZanrModel', back_populates='videohry')
        
class VyvSpolModel(BaseModel):
    __tablename__ = 'vyvspol'
    
    id = Column(BigInteger, Sequence('all_id_seq'), primary_key=True)
    nazev = Column(String)
    zeme = Column(String)
    pocet = Column(Integer)
    
    lastchange = Column(DateTime, default=datetime.datetime.now)
    #externalId = Column(BigInteger, index=True)

    videohry = relationship('VideohraModel', back_populates='vyvspol')
    #zanr = relationship('ZanrModel', secondary=VyvSpolZanrModel, back_populates='vyvspol')
    zamereni = relationship('VyvSpolZanrModel', back_populates='vyvspol')

class ZanrModel(BaseModel):
    __tablename__ = 'zanr'
    
    id = Column(BigInteger, Sequence('all_id_seq'), primary_key=True)
    nazev = Column(String)
    
    lastchange = Column(DateTime, default=datetime.datetime.now)

    videohry = relationship('VideohraModel', back_populates='zanr')
    #vyvspol = relationship('VyvSpolModel', secondary=VyvSpolZanrModel, back_populates='zanr')
    zamereni = relationship('VyvSpolZanrModel', back_populates='zanr')

#BaseModel.metadata.drop_all(engine)
BaseModel.metadata.create_all(engine)

#################
#   SESSION     #
#################

SessionMaker = sessionmaker(bind=engine)
session = SessionMaker()

dbSessionData = {}

def defineStartupAndShutdown(app, SessionMaker):
    @app.on_event("startup")
    async def startup_event():
        session = SessionMaker()
        dbSessionData['session'] = session

    @app.on_event("shutdown")
    def shutdown_event():
        session = dbSessionData.get('session', None)
        if not session is None:
            session.close()

def extractSession(info):
    session = dbSessionData.get('session', None)
    assert not session is None, 'session is not awailable'
    return session

#############
#   CRUD    #
#############

def crudVideohraCreate(db: SessionMaker, videohra):
    VideohraRow = VideohraModel(id=videohra.id, nazev=videohra.nazev, rok=videohra.rok, doba=videohra.doba, obtiznost=videohra.obtiznost, vyvspol_id=videohra.vyvspol_id, zanr_id=videohra.zanr_id)
    db.add(VideohraRow)
    db.commit()
    db.refresh(VideohraRow)
    return VideohraRow

def crudVideohraGet(db: SessionMaker, id: int):
    return db.query(VideohraModel).filter(VideohraModel.id==id).first()

def crudVideohraGetAll(db: SessionMaker, skip: int = 0, limit: int = 100):
    return db.query(VideohraModel).offset(skip).limit(limit).all()


def crudVyvSpolCreate(db: SessionMaker, vyvspol):
    VyvSpolRow = VyvSpolModel(id=vyvspol.id, nazev=vyvspol.nazev, zeme=vyvspol.zeme, pocet=vyvspol.pocet)
    db.add(VyvSpolRow)
    db.commit()
    db.refresh(VyvSpolRow)
    return VyvSpolRow

def crudVyvSpolGet(db: SessionMaker, id: int):
    return db.query(VyvSpolModel).filter(VyvSpolModel.id==id).first()

def crudVyvSpolGetAll(db: SessionMaker, skip: int = 0, limit: int = 100):
    return db.query(VyvSpolModel).offset(skip).limit(limit).all()


def crudZanrCreate(db: SessionMaker, zanr):
    ZanrRow = ZanrModel(id=zanr.id, nazev=zanr.nazev)
    db.add(ZanrRow)
    db.commit()
    db.refresh(ZanrRow)
    return ZanrRow

def crudZanrGet(db: SessionMaker, id: int):
    return db.query(ZanrModel).filter(ZanrModel.id==id).first()

def crudZanrGetAll(db: SessionMaker, skip: int = 0, limit: int = 100):
    return db.query(ZanrModel).offset(skip).limit(limit).all()


def crudZamereniCreate(db: SessionMaker, zamereni):
    ZamereniRow = VyvSpolZanrModel(id=zamereni.id, vyvspol_id=zamereni.vyvspol_id, zanr_id=zamereni.zanr_id)
    db.add(ZamereniRow)
    db.commit()
    db.refresh(ZamereniRow)
    return ZamereniRow

#################################
#   DATA EXTRACTION FROM FILES  #
#################################

def PopulateDatabase():
    with open("./data/vyvspol.txt","r") as file:
        for line in file:
            id, nazev, zeme, pocet = line.strip().split(";")
            data = {'id': f'{id}', 'nazev': f'{nazev}', 'zeme': f'{zeme}', 'pocet': f'{pocet}'}
            crudVyvSpolCreate(db=session, vyvspol=VyvSpolModel(**data))
            #print(data)

    with open("./data/zanr.txt","r") as file:
        for line in file:
            id, nazev = line.strip().split(";")
            data = {'id': f'{id}', 'nazev': f'{nazev}'}
            crudZanrCreate(db=session, zanr=ZanrModel(**data))
            #print(data)

    with open("./data/videohra.txt","r") as file:
        for line in file:
            id, nazev, rok, doba, obtiznost, vyvspol_id, zanr_id = line.strip().split(";")
            data = {'id': f'{id}', 'nazev': f'{nazev}', 'rok': f'{rok}', 'doba': f'{doba}', 'obtiznost': f'{obtiznost}', 'vyvspol_id': f'{vyvspol_id}', 'zanr_id': f'{zanr_id}'}
            crudVideohraCreate(db=session, videohra=VideohraModel(**data))
            #print(data)
            
    with open("./data/zamereni.txt","r") as file:
        for line in file:
            id, vyvspol_id, zanr_id = line.strip().split(";")
            data = {'id': f'{id}', 'vyvspol_id': f'{vyvspol_id}', 'zanr_id': f'{zanr_id}'}
            crudZamereniCreate(db=session, zamereni=VyvSpolZanrModel(**data))

#PopulateDatabase()
session.close()

#############
#   GetAll  #
#############

session = SessionMaker()

###   VIDEOHRA    ###

VideohraData = list(crudVideohraGetAll(db=session))
for index, VideohraRow in enumerate(VideohraData):
    row = crudVideohraGet(db=session, id=VideohraRow.id)
    print(row.id, row.nazev, row.rok, row.doba, row.obtiznost, sep='\t\t')

session.close()

#########################
#   SERVER SETTINGS     #
#########################

servers = {}
_api_process = None

def start_api(app=None, port=9992, runNew=True):
    """Stop the API if running; Start the API; Wait until API (port) is available (reachable)"""
    assert port in [9991, 9992, 9993, 9994], f'port has unexpected value {port}'
    def run():
        uvicorn.run(app, port=port, host='0.0.0.0', root_path='')
        
    _api_process = servers.get(port, None)
    if _api_process:
        _api_process.terminate()
        _api_process.join()
        del servers[port]
    
    if runNew:
        assert (not app is None), 'app is None'
        _api_process = Process(target=run, daemon=True)
        _api_process.start()
        servers[port] = _api_process

#####################
#   GQL MODELS      #
#####################

class ZamereniGQL(graphene.ObjectType):
    id = graphene.ID()
    vyvspol_id = graphene.ID()
    zanr_id = graphene.ID()

    vyvspol = graphene.Field(lambda: VyvSpolGQL)
    
    def resolve_vyvspol(parent, info):
        return parent.vyvspol
    
    zanr = graphene.Field(lambda: ZanrGQL)
    
    def resolve_zanr(parent, info):
        return parent.zanr

class VideohraGQL(graphene.ObjectType):
    id = graphene.ID()
    nazev = graphene.String()
    rok = graphene.Int()
    doba = graphene.String()
    obtiznost = graphene.String()
    lastchange = graphene.DateTime()

    vyvspol = graphene.Field(lambda: VyvSpolGQL)
    
    def resolve_vyvspol(parent, info):
        return parent.vyvspol
    
    zanr = graphene.Field(lambda: ZanrGQL)
    
    def resolve_zanr(parent, info):
        return parent.zanr

class VyvSpolGQL(graphene.ObjectType):
    id = graphene.ID()
    nazev = graphene.String()
    zeme = graphene.String()
    pocet = graphene.Int()
    lastchange = graphene.DateTime()

    videohry = graphene.List(VideohraGQL)
    
    def resolve_videohry(parent, info):
        return parent.videohry
    
    zamereni = graphene.List(lambda: ZamereniGQL)
    
    def resolve_zamereni(parent, info):
        return parent.zamereni

class ZanrGQL(graphene.ObjectType):
    id = graphene.ID()
    nazev = graphene.String()
    lastchange = graphene.DateTime()

    videohry = graphene.List(VideohraGQL)
    
    def resolve_videohry(parent, info):
        return parent.videohry
    
    zamereni = graphene.List(lambda: ZamereniGQL)
    
    def resolve_zamereni(parent, info):
        return parent.zamereni

#############
#   QUERY   #
#############

class QueryGQL(graphene.ObjectType):
    videohra = graphene.Field(VideohraGQL, id = graphene.ID(required = True))
    vyvspol = graphene.Field(VyvSpolGQL, id = graphene.ID(required = True))
    zanr = graphene.Field(ZanrGQL, id = graphene.ID(required = True))
    videohraAll = graphene.List(VideohraGQL, id = graphene.ID(required = False))
    vyvspolAll = graphene.List(VyvSpolGQL, id = graphene.ID(required = False))
    zanrAll = graphene.List(ZanrGQL, id = graphene.ID(required = False))
    
    def resolve_videohra(root, info, id):
        session = extractSession(info)
        result = session.query(VideohraModel).filter(VideohraModel.id==id).first()
        return result
    
    def resolve_vyvspol(root, info, id):
        session = extractSession(info)
        result = session.query(VyvSpolModel).filter(VyvSpolModel.id==id).first()
        return result
    
    def resolve_zanr(root, info, id):
        session = extractSession(info)
        result = session.query(ZanrModel).filter(ZanrModel.id==id).first()
        return result
    
    def resolve_videohraAll(root, info, id):
        session = extractSession(info)
        result = session.query(VideohraModel)
        return result
    
    def resolve_vyvspolAll(root, info, id):
        session = extractSession(info)
        result = session.query(VyvSpolModel)
        return result
    
    def resolve_zanrAll(root, info, id):
        session = extractSession(info)
        result = session.query(ZanrModel)
        return result

#################
#   MUTATIONS   #
#################

###   VIDEOHRA  ###

class CreateVideohraInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    nazev = graphene.String(required=False)
    rok = graphene.Int(required=False)
    doba = graphene.String(required=False)
    obtiznost = graphene.String(required=False)
    vyvspol_id = graphene.ID(required=False)
    zanr_id = graphene.ID(required=False)
    
    def asDict(self):
        return {
            'id': self.id,
            'nazev': self.nazev,
            'rok': self.rok,
            'doba': self.doba,
            'obtiznost': self.obtiznost,
            'vyvspol_id': self.vyvspol_id,
            'zanr_id': self.zanr_id
        }
    
class CreateVideohraGQL(graphene.Mutation):
    class Arguments:
        videohra = CreateVideohraInput(required = True)
    
    ok = graphene.Boolean()
    result = graphene.Field(VideohraGQL)
    
    def mutate(parent, info, videohra):
        session = extractSession(info)
        videohraDict = videohra.asDict()
        videohraRow = VideohraModel(**videohraDict)
        session.add(videohraRow)
        session.commit()
        session.refresh(videohraRow)
        return CreateVideohraGQL(ok=True, result=videohraRow)
    pass

class UpdateVideohraInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    nazev = graphene.String(required=False)
    rok = graphene.Int(required=False)
    doba = graphene.String(required=False)
    obtiznost = graphene.String(required=False)
    vyvspol_id = graphene.ID(required=False)
    zanr_id = graphene.ID(required=False)
    
    def asDict(self):
        return {
            'id': self.id,
            'nazev': self.nazev,
            'rok': self.rok,
            'doba': self.doba,
            'obtiznost': self.obtiznost,
            'vyvspol_id': self.vyvspol_id,
            'zanr_id': self.zanr_id
        }
    
class UpdateVideohraGQL(graphene.Mutation):
    class Arguments:
        videohra = UpdateVideohraInput(required = True)
    
    ok = graphene.Boolean()
    result = graphene.Field(VideohraGQL)
    
    def mutate(parent, info, videohra):
        session = extractSession(info)
        videohraDict = videohra.asDict()
        videohraRow = session.query(VideohraModel).filter(VideohraModel.id==videohra.id).first()
        if videohraDict['nazev'] != None:
            videohraRow.nazev = videohraDict['nazev']
        if videohraDict['rok'] != None:
            videohraRow.rok = videohraDict['rok']
        if videohraDict['doba'] != None:
            videohraRow.doba = videohraDict['doba']
        if videohraDict['obtiznost'] != None:
            videohraRow.obtiznost = videohraDict['obtiznost']
        if videohraDict['vyvspol_id'] != None:
            videohraRow.vyvspol_id = videohraDict['vyvspol_id']
        if videohraDict['zanr_id'] != None:
            videohraRow.zanr_id = videohraDict['zanr_id']
        
        session.commit()     
        session.refresh(videohraRow)
        return CreateVideohraGQL(ok=True, result=videohraRow)
    pass

class DeleteVideohraInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    nazev = graphene.String(required=False)
    
    def asDict(self):
        return {
            'id': self.id,
            'nazev': self.nazev
        }

class DeleteVideohraGQL(graphene.Mutation):
    class Arguments:
        videohra = DeleteVideohraInput(required = True)

    ok = graphene.Boolean()
    result = graphene.Field(VideohraGQL)

    def mutate(parent, info, videohra):
        session = extractSession(info)
        videohraRow = session.query(VideohraModel).filter(VideohraModel.id==videohra.id).first()
        
        session.delete(videohraRow)
        session.commit()     
        return CreateVideohraGQL(ok=True, result=videohraRow)
    pass

###   VYVSPOL   ###

class CreateVyvSpolInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    nazev = graphene.String(required=False)
    zeme = graphene.String(required=False)
    pocet = graphene.Int(required=False)
    
    def asDict(self):
        return {
            'id': self.id,
            'nazev': self.nazev,
            'zeme': self.zeme,
            'pocet': self.pocet
        }
    
class CreateVyvSpolGQL(graphene.Mutation):
    class Arguments:
        vyvspol = CreateVyvSpolInput(required = True)
    
    ok = graphene.Boolean()
    result = graphene.Field(VyvSpolGQL)
    
    def mutate(parent, info, vyvspol):
        session = extractSession(info)
        vyvSpolDict = vyvspol.asDict()
        vyvSpolRow = VyvSpolModel(**vyvSpolDict)
        session.add(vyvSpolRow)
        session.commit()
        session.refresh(vyvSpolRow)
        return CreateVyvSpolGQL(ok=True, result=vyvSpolRow)
    pass

class UpdateVyvSpolInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    nazev = graphene.String(required=False)
    zeme = graphene.String(required=False)
    pocet = graphene.Int(required=False)
    
    def asDict(self):
        return {
            'id': self.id,
            'nazev': self.nazev,
            'zeme': self.zeme,
            'pocet': self.pocet
        }
    
class UpdateVyvSpolGQL(graphene.Mutation):
    class Arguments:
        vyvspol = UpdateVyvSpolInput(required = True)
    
    ok = graphene.Boolean()
    result = graphene.Field(VyvSpolGQL)
    
    def mutate(parent, info, vyvspol):
        session = extractSession(info)
        vyvSpolDict = vyvspol.asDict()
        vyvSpolRow = session.query(VyvSpolModel).filter(VyvSpolModel.id==vyvspol.id).first()
        if vyvSpolDict['nazev'] != None:
            vyvSpolRow.nazev = vyvSpolDict['nazev']
        if vyvSpolDict['zeme'] != None:
            vyvSpolRow.zeme = vyvSpolDict['zeme']
        if vyvSpolDict['pocet'] != None:
            vyvSpolRow.pocet = vyvSpolDict['pocet']
        
        session.commit()     
        session.refresh(vyvSpolRow)
        return CreateVyvSpolGQL(ok=True, result=vyvSpolRow)
    pass

class DeleteVyvSpolInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    nazev = graphene.String(required=False)
    
    def asDict(self):
        return {
            'id': self.id,
            'nazev': self.nazev
        }

class DeleteVyvSpolGQL(graphene.Mutation):
    class Arguments:
        vyvspol = DeleteVyvSpolInput(required = True)

    ok = graphene.Boolean()
    result = graphene.Field(VyvSpolGQL)

    def mutate(parent, info, vyvspol):
        session = extractSession(info)
        vyvSpolRow = session.query(VyvSpolModel).filter(VyvSpolModel.id==vyvspol.id).first()
        
        session.delete(vyvSpolRow)
        session.commit()     
        return CreateVyvSpolGQL(ok=True, result=vyvSpolRow)
    pass

###   ZANR  ###

class CreateZanrInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    nazev = graphene.String(required=False)
    
    def asDict(self):
        return {
            'id': self.id,
            'nazev': self.nazev
        }
    
class CreateZanrGQL(graphene.Mutation):
    class Arguments:
        zanr = CreateZanrInput(required = True)
    
    ok = graphene.Boolean()
    result = graphene.Field(ZanrGQL)
    
    def mutate(parent, info, zanr):
        session = extractSession(info)
        zanrDict = zanr.asDict()
        zanrRow = ZanrModel(**zanrDict)
        session.add(zanrRow)
        session.commit()
        session.refresh(zanrRow)
        return CreateZanrGQL(ok=True, result=zanrRow)
    pass

class UpdateZanrInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    nazev = graphene.String(required=False)
    
    def asDict(self):
        return {
            'id': self.id,
            'nazev': self.nazev
        }
    
class UpdateZanrGQL(graphene.Mutation):
    class Arguments:
        zanr = UpdateZanrInput(required = True)
    
    ok = graphene.Boolean()
    result = graphene.Field(ZanrGQL)
    
    def mutate(parent, info, zanr):
        session = extractSession(info)
        zanrDict = zanr.asDict()
        zanrRow = session.query(ZanrModel).filter(ZanrModel.id==zanr.id).first()
        if zanrDict['nazev'] != None:
            zanrRow.nazev = zanrDict['nazev']
        
        session.commit()     
        session.refresh(zanrRow)
        return CreateZanrGQL(ok=True, result=zanrRow)
    pass

class DeleteZanrInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    nazev = graphene.String(required=False)
    
    def asDict(self):
        return {
            'id': self.id,
            'nazev': self.nazev
        }

class DeleteZanrGQL(graphene.Mutation):
    class Arguments:
        zanr = DeleteZanrInput(required = True)

    ok = graphene.Boolean()
    result = graphene.Field(ZanrGQL)

    def mutate(parent, info, zanr):
        session = extractSession(info)
        zanrRow = session.query(ZanrModel).filter(ZanrModel.id==zanr.id).first()
        
        session.delete(zanrRow)
        session.commit()     
        return CreateZanrGQL(ok=True, result=zanrRow)
    pass

###   ZAMERENI  ###

class CreateZamereniInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    vyvspol_id = graphene.ID(required=False)
    zanr_id = graphene.ID(required=False)
    
    def asDict(self):
        return {
            'id': self.id,
            'vyvspol_id': self.vyvspol_id,
            'zanr_id': self.zanr_id
        }

class CreateZamereniGQL(graphene.Mutation):
    class Arguments:
        zamereni = CreateZamereniInput(required = True)
    
    ok = graphene.Boolean()
    result = graphene.Field(ZamereniGQL)
    
    def mutate(parent, info, zamereni):
        session = extractSession(info)
        zamereniDict = zamereni.asDict()
        zamereniRow = VyvSpolZanrModel(**zamereniDict)
        session.add(zamereniRow)
        session.commit()
        session.refresh(zamereniRow)
        return CreateZamereniGQL(ok=True, result=zamereniRow)
    pass

class UpdateZamereniInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    vyvspol_id = graphene.ID(required=False)
    zanr_id = graphene.ID(required=False)
    
    def asDict(self):
        return {
            'id': self.id,
            'vyvspol_id': self.vyvspol_id,
            'zanr_id': self.zanr_id
        }
    
class UpdateZamereniGQL(graphene.Mutation):
    class Arguments:
        zamereni = UpdateZamereniInput(required = True)
    
    ok = graphene.Boolean()
    result = graphene.Field(ZamereniGQL)
    
    def mutate(parent, info, zamereni):
        session = extractSession(info)
        zamereniDict = zamereni.asDict()
        zamereniRow = session.query(VyvSpolZanrModel).filter(VyvSpolZanrModel.id==zamereni.id).first()
        if zamereniDict['vyvspol_id'] != None:
            zamereniRow.vyvspol_id = zamereniDict['vyvspol_id']
        if zamereniDict['zanr_id'] != None:
            zamereniRow.zanr_id = zamereniDict['zanr_id']
        
        session.commit()     
        session.refresh(zamereniRow)
        return CreateZamereniGQL(ok=True, result=zamereniRow)
    pass

class DeleteZamereniInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    
    def asDict(self):
        return {
            'id': self.id
        }

class DeleteZamereniGQL(graphene.Mutation):
    class Arguments:
        zamereni = DeleteZamereniInput(required = True)

    ok = graphene.Boolean()
    result = graphene.Field(ZamereniGQL)

    def mutate(parent, info, zamereni):
        session = extractSession(info)
        zamereniRow = session.query(VyvSpolZanrModel).filter(VyvSpolZanrModel.id==zamereni.id).first()
        
        session.delete(zamereniRow)
        session.commit()     
        return CreateZamereniGQL(ok=True, result=zamereniRow)
    pass

###   MUTATIONS CLASS   ###

class Mutations(graphene.ObjectType):
    create_videohra = CreateVideohraGQL.Field()
    update_videohra = UpdateVideohraGQL.Field()
    delete_videohra = DeleteVideohraGQL.Field()
    
    create_vyvspol = CreateVyvSpolGQL.Field()
    update_vyvspol = UpdateVyvSpolGQL.Field()
    delete_vyvspol = DeleteVyvSpolGQL.Field()
    
    create_zanr = CreateZanrGQL.Field()
    update_zanr = UpdateZanrGQL.Field()
    delete_zanr = DeleteZanrGQL.Field()
    
    create_zamereni = CreateZamereniGQL.Field()
    update_zamereni = UpdateZamereniGQL.Field()
    delete_zamereni = DeleteZamereniGQL.Field()

#############################
#   GRAPHQL INTERFACE FIX   #
#############################

'''
def singleCache(f):
    cache = None
    def decorated():
        nonlocal cache
        if cache is None:
            fResult = f()
            cache = fResult.replace('https://swapi-graphql.netlify.app/.netlify/functions/index', '/gql')
        else:
            #print('cached')
            pass
        return cache
    return decorated

@singleCache
def getSwapi():
    source = "https://raw.githubusercontent.com/graphql/swapi-graphql/master/public/index.html"
    r = requests.get(source)
    return r.text
'''

#####################
#   APP SETTINGS    #
#####################

graphql_app = GraphQLApp(
    schema=graphene.Schema(query=QueryGQL, mutation=Mutations), 
    on_get=make_graphiql_handler())

app = FastAPI()#root_path='/api')

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:31102",
    "null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

defineStartupAndShutdown(app, SessionMaker)

app.add_route('/gql/', graphql_app)

#@app.get('/gql', response_class=fastapi.responses.HTMLResponse)
#def swapiUI():
#    return getSwapi()

### APP START   ###
start_api(app=app, port=9992, runNew=True)

### APP FINISH  ###
start_api(app=app, port=9992, runNew=False)