from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from flask_appbuilder.filemanager import get_file_original_name
from helpers import comments
from flask import Markup, url_for

"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
def style_it(item):
    style = {
                'Text Box': '<span style="color:#97ad66; font-size:larg; margin-left:7px;"><i class="far fa-comment-alt"></i></span>',
                'Call-out': '<span style="color:#ad669d; font-size:larg; margin-left:7px;"><i class="fas fa-bullhorn"></i></span>',
                'Callout': '<span style="color:#ad669d; font-size:larg; margin-left:7px;"><i class="fas fa-bullhorn"></i></span>',
                'Cloud+': '<span style="color:#3ec3cc; font-size:larg; margin-left:7px;"><i class="fas fa-cloud"></i></span>',
            }
    try:
        return style[item.style]
    except:
        return 'ND'

class Document(AuditMixin, Model):
    id = Column(Integer, primary_key= True)
    unit = Column(String(3), nullable=False)
    materialclass = Column(String(1), nullable=False)
    doctype = Column(String(3), nullable=False)
    serial = Column(String(5), nullable=False)
    partner = Column(String(3), nullable=False)
    sheet = Column(String(3))

    def __repr__(self):
        name = '-'.join([self.unit, self.materialclass,
                        self.doctype, self.serial, self.sheet])
        return name

    def name(self):
        name = '-'.join([self.unit, self.materialclass,
                        self.doctype, self.serial, self.sheet])
        return name

    def comment(self):
        return self.comments
    
    def revision(self):
        return str(self.revision)
    
    def count(self):
        return len(self.comments)
    
    def count_included(self):
        count = 0
        for comment in self.comments:
            if comment.included:
                count += 1
        return count
    
    def count_closed(self):
        count = 0
        for comment in self.comments:
            if comment.closed:
                count += 1
        return count
    
    def count_no_reply(self):
        count = 0
        for comment in self.comments:
            if comment.reply == " " and comment.included == False:
                count += 1
        return count

    def count_open(self):
        count_open = self.count() - self.count_closed()
        return count_open
    
    def pretty_date(self):
        return self.created_on.strftime('%d, %b %Y')

class Revisions(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    file = Column(FileColumn, nullable=False)
    revision = Column(String(30))
    trasmittal = Column(String(30), nullable=False)
    date_trs = Column(Date, nullable=False)
    note = Column(String(250))
    document_id = Column(Integer, ForeignKey('document.id'), nullable=False)
    document = relationship(Document, backref='revision')
    reply = Column(Boolean, default=False)

    def __repr__(self):
        if self.reply:
            return self.revision +"-Reply"
        return self.revision

    def file_name(self):
        return get_file_original_name(str(self.file))


    def download(self):
        return Markup(
            '<a href="' + url_for('RevisionView.download', filename=str(self.file)) + '">Download</a>')

    def pretty_date(self):
        return self.created_on.strftime('%d, %b %Y')
    
    def pretty_revision(self):
        if self.reply:
            return self.revision +"-Reply"
        return self.revision

class Comments(AuditMixin, Model):
    id = Column(Integer, primary_key= True)
    id_c = Column(Integer)
    style = Column(String(30), default='no type')
    author = Column(String(100), default='no author')
    comment = Column(String(500), default='no comment')
    reply = Column(String(500), default='no reply')
    included = Column(Boolean, default=False)
    closed = Column(Boolean, default=False)
    type_reply = Column(Boolean, default=False)
    document_id = Column(Integer, ForeignKey('document.id'))
    document = relationship(Document, backref='comments')
    revision_id = Column(Integer, ForeignKey('revisions.id'))
    revision = relationship(Revisions, backref='comments')
    page = Column(String(30), default ='-' )
    partner = Column(String(3), nullable=False)
    note = Column(String(250))

    def __repr__(self):
        return self.comment
    
    def pretty_style(self):
        
        try:
            return Markup(style_it(self))
        except:
            return Markup('<i class="far fa-question-circle"></i>')
    
    def pretty_closed(self):
        try:
            if self.closed == True:
                return Markup('<span style="color:#519a6c; font-size:larger"><i class="fas fa-thumbs-up"></i>')
            return Markup('<span style="color:#dddddd; font-size:larger"><i class="fas fa-thumbs-up"></i>')
        except:
            pass
    
    def pretty_included(self):
        try:
            if self.included == True:
                return Markup('<span style="color:#7b66ad; font-size:larger"><i class="fas fa-check"></i>')
            return Markup('<span style="color:#dddddd; font-size:larger"><i class="fas fa-check"></i>')
        except:
            pass
    
    def doc(self):
        
        return str(self.document)
    
    def pretty_comment(self):
        return self.comment[:75]

    def pretty_reply(self):
        
        return self.reply[:75]
    
    def pretty_date(self):
        return self.created_on.strftime('%d, %b %Y')
    
    #def pretty_revision(self):
        #return self.revision.revision

    def open_comments(self):
        if self.closed == True:
            return False
        return True