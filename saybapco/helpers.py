import openpyxl, re
from config import UPLOAD_FOLDER
from app import db, models
from flask_appbuilder.filemanager import get_file_original_name
from openpyxl.styles import Font, Color
from openpyxl.worksheet.table import Table, TableStyleInfo
import uuid
#from views import Report
from flask import render_template, abort


rev_order = ['A','B','C','D','E','F','G','H','I','L','M','N','O','P','Q','R','S','T',
                'U','V','Z','0','1','2','3','4','5','6','7','8','9','10']

def parse_escaped_character_match(match):
    return chr(int(match.group(1), 16))

def sanetext(input_string):
    if input_string is not None:
        return re.sub("_x([0-9A-F]{4})_", parse_escaped_character_match, str(input_string))
    return " "


#
#  Add Revisions uploading a Comment file by Bluebin.
#


def check_duplicates():
    revision = models.Revisions
    rev_list = db.session.query(revision).all()
    
    seen = {}
    dupes = []

    for rev in rev_list:
        rev_key = str(rev.document) + str(rev.revision)

        if rev.reply:
            rev_key = str(rev.document) + str(rev.revision) + "-Reply"

            
        
        if rev_key not in seen:
            seen[rev_key] = 1
        else:
            if seen[rev_key] == 1:
                dupes.append(rev_key)
            seen[rev_key] += 1
    print('seen',len(seen))
    print('dupes',len(dupes))
    for s in range(10):
        for s in seen:
            print(s)
    print('dupes', dupes)

def comments(item):
    try:
        print('file processed:', str(item.file))
        
        #print('file processed:', file)

        #file = open('/Users/dp/py3/saybapco/saybapco/comments/019-C-GAD-10010-001-RAP-CS REPLY.xlsx', mode='rb')
        #filename = '019-C-GAD-10010-001-RAP-CS REPLY.xlsx'

        filename = get_file_original_name(item.file)
        unit = filename[0:3]

        #partner = filename[4]

        mat = filename[4]
        doctype = filename[6:9]
        serial = filename[10:15]
        type_reply = False

        
        #if filename[26:29] == "REP":
        if filename[-8:-5] == "REP":
            print('Reply identification: ', filename[-8:-5] )
            type_reply = True
            
            
    except:
        abort(400,'Please check your file name.')
    
    try:
        print(UPLOAD_FOLDER)
        file = open(UPLOAD_FOLDER + item.file, mode='rb')
        print('arianna is here')
        print(UPLOAD_FOLDER)
        wb = openpyxl.load_workbook(file)
        ws = wb.active

        session = db.session
        comments= models.Comments
        documents = models.Document
        revisions = models.Revisions

        revision = session.query(revisions).filter(revisions.revision == item.revision, revisions.document_id == item.document_id).first()
        #revision = session.query(revisions).filter(revisions.id == item.id).first()
        session.query(comments).filter(comments.document_id == item.document_id, comments.revision_id == revision.id).delete()
    
        #print('doc id',item.document_id,'rev id', revision.id, 'item id', item.id)
        comm_list = session.query(comments).filter(comments.document_id == item.document_id, comments.revision_id == revision.id).all()
        #print('the comments len is:', len(comm_list))
        session.query(comments).filter(comments.document_id == item.document_id, comments.revision_id == revision.id).delete()
        #print('delete query executed')
        
    except:
        abort(400,'Please check your Excel file format.')
    

    #session.commit()
    #check columns label
    #for row in ws.iter_colum()
    #print('document id', item.document_id,'revision:', item.id)
    
    partner = item.partner
    print('here')
    #revision = item.revision
    try:
        
        for row in ws.iter_rows(min_row=2):
            #print(row[0].value, row[1].value, row[2].value,
                #row[3].value, row[4].value, row[5].value, row[6].value, row[7].value)
            if row[0].value is not None:
                #print('row 0 in not null', row[0].value)
                


                id_c = sanetext(row[0].value)
                style = sanetext(row[1].value)
                page = sanetext(row[2].value)
                author = sanetext(row[3].value)
                comment = sanetext(row[4].value)
                reply = sanetext(row[5].value)
                included = sanetext(row[6].value)
                closed = sanetext(row[7].value)


                #print(id_c, style, author)
                


                if closed == 'Y':
                    closed = True
                else:
                    closed = False
                
                if included == 'Y':
                    included = True
                    closed = True
                else:
                    included = False
                                
                #print('before comment')
                #print('document id', item.document_id,'revision:', item.id)
                comm = comments(id_c=id_c, partner=partner, style=style, page=page, author=author, comment=comment,
                                reply=reply, included=included, closed=closed,
                                document_id=item.document_id, revision_id=item.id, type_reply=type_reply)
                
                session.add(comm)

                #print('after comment')
            
                
    except:
        abort(400,'Please check your Excel file format.')
    
    session.commit()
    #session.close()
    
    return 'done'

def last_rev(self, item):

    # trova tutte le revisioni per il documento
    doc = item.document
    rev = item.revision
    print('last rev function:')
    print('document ID', doc.id)
    print('revisions', doc.revision)
    print('doc rev', rev)
    print('is a reply?', item.reply)
    #revisions = db.session.query(models.Revisions).filter(models.Revisions.document_id == item.id).all()
    #print('revision list', revisions)
    cur_rev_index = rev_order.index(rev)
    doc_rev_index_list = []
    for rev in item.revision:
        doc_rev_index_list.append(rev_order.index(rev))
    if cur_rev_index < max(doc_rev_index_list):
        print('This REV is SUPERSEEDED')

def set_current(self, item):
    print('set current function start')
    print(item.document)
    doc = item.document
    try:
        print(doc.id)
        #print(doc.document_id)
        
        #comme = db.session.query(models.Comments).filter(models.Comments.document_id == doc.id).all()
        #print(comme)
        db.session.query(models.Comments).filter(models.Comments.document_id == doc.id).delete()
        #db.session.query(models.Comments).filter(models.Comments.document_id == item.document_id).delete()
        
        print('not here')
        comments(item)
        print(doc.revision)
        for rev in doc.revision:
            print(rev)
            rev.current = False
        item.current = True
        db.session.commit()
    except:
        print('something wrong in set current')
        pass

def precheck_doc(self, item):
    filename = get_file_original_name(item.file)
    filename_list = filename.split('-',6)

    try:
        filename_list = filename.split('-')
        print(len(filename_list), filename)
        if len(filename_list) != 7:
            return False, "Please check your File Name: " + filename
         
        rev = models.Revisions
        this_reply = False
        if filename_list[6] == 'CS REP.xlsx':
            this_reply = True
        
        print('rev.reply == item.reply',rev.reply, item.reply)
        revision = db.session.query(rev).filter(rev.document_id == item.document_id, rev.revision == item.revision, rev.reply == this_reply).first()
        print(filename_list[6])

        this_rev = item.revision
        if filename_list[6] == 'CS REP.xlsx':
            this_rev = this_rev + '-Reply'
        

        print('revision',revision, 'item rev', this_rev)
        if str(this_rev) == str(revision):
            return False, "The Revision {0} already exist.".format(this_rev)

    except:
        return False, "Something Wrong Whit Your File Name: " + filename

    try:
        if this_rev != "A":
            last_rev(self, revision)
    except:
        print('something worng with last rev function')
        pass

    return True, "File uploaded " + filename

def check_Doc(self, item):
    try:
        print('here in check doc', item.file)
        filename = get_file_original_name(item.file)
        filename_list = filename.split('-',6)
        
        
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
            #session.close()
            return document.id, document.partner
        
        else:
            document = doc(unit=unit, materialclass=mat, doctype=doctype, 
                        serial=serial, sheet=sheet, partner=partner)
            
            session.add(document)

            session.flush()
            session.commit()
            #session.close()

            return document.id, document.partner
    except:
        abort(400,'Please check your file name. - check_Doc')

def precheck_reply(self,item):
    filename = get_file_original_name(item.file)
    filename_list = filename.split('-',6)
    print('len:',len(filename_list), filename_list[6])
    try:
        if filename_list[6] != 'CS REP.xlsx':
            return False, "Something Wrong Whit Your File Name: " + filename_list[6]
    except:
        return False, "Something is wrong with your file name. " + filename


def check_reply(self, item):
    filename = get_file_original_name(item.file)
    try:
        print('this is the Check reply Functions....')
        print('Reply identification: ', filename[-8:-5] )
        if filename[-8:-5] == "REP":
            return True
    except:
        return False

def check_doc_closed(doc_id):
    doc = models.Document
    document = db.session.query(doc).filter(doc.id==doc_id).first()
    print('Check Doc Closed Function')
    
    closed = True
    for com in document.comments:
        
        if com.closed == False:
            closed = False
            break
        print('comment closed:',com, com.closed)
    document.closed = closed
    document.changed_by_fk = '1'
    db.session.commit()
    #db.session.close()

def set_comments_blank():
    comment = models.Comments
    revision = models.Revisions
    document = models.Document
    
    session = db.session

    revision_reply = session.query(revision).filter(revision.reply == True).all()
    print('the number of revisions in reply is:', len(revision_reply))
    blank_reply = 0
    for rev in revision_reply:
        #session = db.session
        comments_reply = rev.comments

    
        print('the number of comments in reply is:', len(comments_reply))

        for comment in comments_reply:
            
            if comment.reply == ' ' and comment.comment == ' ':
                print('id\t', comment.id, 'autho\t', comment.author, '\tcomm', comment.comment[:15])
                comment.note = 'No comment AND No replies'
                comment.changed_by_fk = '1'
                session.delete(comment)
                blank_reply += 1
                print('*************   NO Comment AND NO Reply   *************')
      
            session.commit()
    
    comment = models.Comments
    comment_all = session.query(comment).all()
    blank = 0
    for comment in comment_all:

        if comment.comment == ' ':
            blank += 1
            print('blank comment')
            session.delete(comment)
    session.commit()
    print('vuoti', blank)
    print('vuoti in reply', blank_reply)
    session.close()
    

def set_comments_included():
    comment = models.Comments
    revision = models.Revisions
    document = models.Document
    
    session = db.session

    # Take only revisions in reply
    revision_reply = session.query(revision).filter(revision.reply == True).all()
    print('the number of revisions in reply is:', len(revision_reply))
    
    # for every revision take the comments
    closed_by_included = 0
    for rev in revision_reply:

        comments_reply = rev.comments
    
        print('the number of comments in reply is:', len(comments_reply))

        # for every comments do things

        for comment in comments_reply:
            print('id\t', comment.id, 'autho\t', comment.author, '\tcomm', comment.comment[:15])
            
            # At this Conditions
            
            if comment.included:
                comment.closed = True
                closed_by_included += 1
                comment.changed_by_fk = '1'
                
                print('*************   Comment Included --> Closed   *************')
            
            
            session.commit()
    print('closed_by_included', closed_by_included)
    session.close()

def report_all():
    file_template = UPLOAD_FOLDER + 'report/cs_dashboard.xlsx'
    filepath = UPLOAD_FOLDER + 'report/' + str(uuid.uuid4()) + 'cs_dashboard.xlsx'
    workbook = openpyxl.load_workbook(file_template)
    
    comment = models.Comments
    revision = models.Revisions
    document = models.Document

    wc = workbook['Comments']    
    wr = workbook['Revisions']
    wd = workbook['Documents']

    # 
    # Styles
    #

    ft = Font(bold=True, color='4b1f68')

    # 
    # Populate Comments Sheet
    #

    '''
    comments = db.session.query(comment).all()
    
    row = 1
    col = 1 

    for comment in comments:
        print('comments *********************')
        _ = wc.cell(column=1, row=row, value=str(comment.id))
        _ = wc.cell(column=2, row=row, value=str(comment.partner))
        _ = wc.cell(column=3, row=row, value=str(comment.document))
        _ = wc.cell(column=4, row=row, value=str(comment.revision))
        _ = wc.cell(column=5, row=row, value=str(comment.included))
        _ = wc.cell(column=6, row=row, value=str(comment.closed))

        row += 1
    '''

    # 
    # Populate revisions Sheet
    #

    
    revisions = db.session.query(revision).all()
    
    row = 1
    col = 1 

    for revision in revisions:
        _ = wr.cell(column=1, row=row, value=str(revision.id))
        _ = wr.cell(column=2, row=row, value=str(revision.file))
        _ = wr.cell(column=3, row=row, value=str(revision.revision))
        _ = wr.cell(column=4, row=row, value=str(revision.trasmittal))
        _ = wr.cell(column=5, row=row, value=str(revision.date_trs))
        _ = wr.cell(column=6, row=row, value=str(revision.document))
        _ = wr.cell(column=7, row=row, value=str(revision.reply))

        row += 1

    # 
    # Populate documents Sheet
    #

    # 
    # Set the labels for the document sheet
    #
    
    documents = db.session.query(document).all()
    
    
    _ = wd.cell(column=1, row=1, value='ID')
    _.font = ft
    _ = wd.cell(column=2, row=1, value='Bapco Code')
    _.font = ft
    _ = wd.cell(column=3, row=1, value='Partner')
    _.font = ft
    _ = wd.cell(column=4, row=1, value='Revisions')
    _.font = ft
    _ = wd.cell(column=5, row=1, value='Open CS')
    _.font = ft
    
    

    # 
    # Set the rows for the document sheet
    #
    
    row = 2
    

    for document in documents:
        doc = [document.id, document.name(), document.partner, str(document.revision), document.count_open()]
        wd.append(doc)
        
        '''
        _ = wd.cell(column=1, row=row, value=str(document.id))
        _ = wd.cell(column=2, row=row, value=str(document.name()))
        _ = wd.cell(column=3, row=row, value=str(document.partner))
        _ = wd.cell(column=4, row=row, value=str(document.revision))
        _ = wd.cell(column=5, row=row, value=str(document.count_open()))
        '''
        

        row += 1
    wd.page_setup.fitToWidth = 1
    
    tab = Table(displayName='Documents', ref='A1:E'+ str(row))
    style = TableStyleInfo(name='TableStyleMedium9')
    tab.tableStyleInfo = style
    #wd.add_table(tab)
    
    workbook.save(filepath) 
    
    file = filepath
    #print(file.name)
    db.session.close()
    return file

def check_doc_closed2():
    doc = models.Document
    documents = db.session.query(doc).all()
    
    for document in documents:

        print('Check Doc Function')
        closed = True
        for com in document.comments:
            
            if com.closed == False:
                closed = False
                break
            print('comment closed:',com, com.closed)
        document.closed = closed
        document.changed_by_fk = '1'
        db.session.commit()
    db.session.close()
        #return True