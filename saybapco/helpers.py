import openpyxl, re
from config import UPLOAD_FOLDER
from app import db, models
from flask_appbuilder.filemanager import get_file_original_name


def parse_escaped_character_match(match):
    return chr(int(match.group(1), 16))

def sanetext(input_string):
    if input_string is not None:
        return re.sub("_x([0-9A-F]{4})_", parse_escaped_character_match, str(input_string))
    return " "


#
#  Add Revisions uploading a Comment file by Bluebin.
#


def comments(item):

    print('file processed:', str(item.file))
    file = open(UPLOAD_FOLDER + item.file, mode='rb')
    print('file processed:', file)

    #file = open('/Users/dp/py3/saybapco/saybapco/comments/019-C-GAD-10010-001-RAP-CS REPLY.xlsx', mode='rb')
    #filename = '019-C-GAD-10010-001-RAP-CS REPLY.xlsx'

    filename = get_file_original_name(item.file)
    unit = filename[0:3]

    #partner = filename[4]

    mat = filename[4]
    doctype = filename[6:9]
    serial = filename[10:15]
    type_reply = False

    try:
        print('Reply identification: ', filename[-8:-5] )
        #if filename[26:29] == "REP":
        if filename[-8:-5] == "REP":
            type_reply = True
    except:
        pass
    
    wb = openpyxl.load_workbook(file)
    ws = wb.active

    session = db.session
    comments= models.Comments
    documents = models.Document
    revisions = models.Revisions

    revision = session.query(revisions).filter(revisions.revision == item.revision, revisions.document_id == item.document_id).first()
    #revision = session.query(revisions).filter(revisions.id == item.id).first()

    try:
        print('doc id',item.document_id,'rev id', revision.id, 'item id', item.id)
        session.query(comments).filter(comments.document_id == item.document_id, comments.revision_id == revision.id).delete()
    except:
        print('some problem here')
        pass
    

    #session.commit()
    #check columns label
    #for row in ws.iter_colum()
    
    partner = item.partner
    #revision = item.revision

    for row in ws.iter_rows(min_row=2):
        print(row[0].value, row[1].value, row[2].value,
              row[3].value, row[4].value, row[5].value, row[6].value, row[7].value)
        if row[0].value is not None:
            print('row 0 in not null', row[0].value)
            try:


                id_c = sanetext(row[0].value)
                style = sanetext(row[1].value)
                page = sanetext(row[2].value)
                author = sanetext(row[3].value)
                comment = sanetext(row[4].value)
                reply = sanetext(row[5].value)
                included = sanetext(row[6].value)
                closed = sanetext(row[7].value)


                print(id_c, style, author)
                


                if closed == 'Y':
                    closed = True
                else:
                    closed = False
                
                if included == 'Y':
                    included = True
                else:
                    included = False
                                
                print('before comment')
                comm = comments(id_c=id_c, partner=partner, style=style, page=page, author=author, comment=comment,
                                reply=reply, included=included, closed=closed,
                                document_id=item.document_id, revision_id=item.id, type_reply=type_reply)
                
                session.add(comm)

                print('after comment')
            
                
            except:
                print('something is None')
                pass
    
        session.commit()
    return 'done'

def check_Doc(self, item):
    filename = get_file_original_name(item.file)
    unit = filename[0:3]
    partner = item.trasmittal[4:7]
    mat = filename[4]
    doctype = filename[6:9]
    serial = filename[10:15]
    sheet = filename[16:19]


    session = db.session
    doc = models.Document
    document = session.query(doc).filter(doc.unit == unit, doc.materialclass == mat,
                                 doc.doctype == doctype, doc.serial == serial, doc.sheet == sheet).first()

    if document:
        return document.id, document.partner
    else:
        document = doc(unit=unit, materialclass=mat, doctype=doctype, 
                       serial=serial, sheet=sheet, partner=partner)
        
        session.add(document)

        session.flush()

        return document.id, document.partner
    

def check_reply(self, item):
    filename = get_file_original_name(item.file)
    try:
        print('this is the Check reply Functions....')
        print('Reply identification: ', filename[-8:-5] )
        if filename[-8:-5] == "REP":
            return True
    except:
        return False
    
    
    
