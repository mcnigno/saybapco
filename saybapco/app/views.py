from flask import render_template, redirect
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import (ModelView, IndexView, BaseView, expose, MasterDetailView, 
                              DirectByChartView, GroupByChartView, CompactCRUDMixin, MultipleView)
from app import appbuilder, db
from .models import Document, Comments, Revisions, Revision_type
from helpers import (comments, check_Doc, check_reply, set_comments_blank, set_comments_included, 
                    report_all, check_doc_closed, check_doc_closed2, check_duplicates, precheck_doc,
                    set_current, report_url, set_position, action_include_close, action_close
                    )
from flask_appbuilder.widgets import (ListBlock, ListCarousel, ListMasterWidget, 
                                        ListThumbnail, SearchWidget, ShowBlockWidget,
                                        ShowVerticalWidget)

from flask_appbuilder.models.group import aggregate_count, aggregate_sum, aggregate_avg, aggregate_count
from flask_appbuilder import action, has_access, permission_name
from flask_appbuilder.filemanager import get_file_original_name
from mass_update import transmittall
from flask import request, send_file
from config import UPLOAD_FOLDER
from flask_appbuilder.models.sqla.filters import FilterStartsWith, FilterEqualFunction, FilterEqual, FilterNotContains
from mass_update import test_closed, reply_rev, find_action, last_rev
from flask import flash, abort, Response, g, url_for, session
from flask_appbuilder.widgets import ListThumbnail, ListBlock
from .customwidgets import ShowDocument

def get_user():
    return g.user

def get_last_doc():
        return g.last_document

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
       
#
#class UploadComments(BaseView):
#    default_view = 'upload'
#    @expose('/upload', methods=('POST','GET'))
#    def upload(self):
#        return self.render_template('upload.html')
class Report(BaseView):
    default_view = 'fileinfo'
    @expose('/fileinfo', methods=['POST', 'GET'])
    def fileinfo(self):
        print('fileinfo')
        #print(request.submit.value)
        if request.method == 'POST':
            print('post')
            print('POST', request.data) 
        #report_url(self)
        return self.render_template('fileinfo.html')
    
    @expose('/forward/', methods=['POST', 'GET'])
    def forward(self):
        print('forward')
        #print(request.submit.value)
        if request.method == 'POST':        
            print('forward')
            print('forward')
            ws = report_all()
            return send_file(ws, as_attachment=True)
        return self.render_template('reports.html')

class CsRepliesView(BaseView):
    default_view = 'csreplies'
    @expose('/csreplies', methods=['POST', 'GET'])
    def csreplies(self):
        print('csreplies')
        #print(request.submit.value)
        if request.method == 'POST':
            print('post')
            print('POST', request.data) 
        #report_url(self)
        return self.render_template('csreplies.html')
    
    @expose('/csreplies_rep/', methods=['POST', 'GET'])
    def csreplies_rep(self):
        print('csreplies_rep')
        #print(request.submit.value)
        if request.method == 'POST':        
            print('csreplies_rep')
            print('csreplies_rep')
            ws = report_all()
            return send_file(ws, as_attachment=True)
        return self.render_template('reports.html')

class CsDashboardView(BaseView):
    default_view = 'csdashboard'
    @expose('/csdashboard', methods=['POST', 'GET'])
    def csdashboard(self):
        print('csdashboard') 
        #print(request.submit.value)
        if request.method == 'POST':
            print('post')
            print('POST', request.data) 
        #report_url(self)
        return self.render_template('csdashboard.html')
    
    @expose('/csdashboard_rep/', methods=['POST', 'GET'])
    def csdashboard_rep(self):
        print('csdashboard_rep')
        #print(request.submit.value)
        if request.method == 'POST':        
            print('csdashboard_rep')
            print('csdashboard_rep')
            ws = report_all()
            return send_file(ws, as_attachment=True)
        return self.render_template('reports.html')

class CsTimeDashView(BaseView):
    default_view = 'cstimedash'
    @expose('/cstimedash', methods=['POST', 'GET'])
    def cstimedash(self):
        print('cstimedash') 
        #print(request.submit.value)
        if request.method == 'POST':
            print('post')
            print('POST', request.data) 
        #report_url(self)
        return self.render_template('cstimedash.html')
    
    @expose('/cstimedash_rep/', methods=['POST', 'GET'])
    def cstimedash_rep(self):
        print('cstimedash_rep')
        #print(request.submit.value)
        if request.method == 'POST':        
            print('cstimedash_rep')
            print('cstimedash_rep')
            ws = report_all()
            return send_file(ws, as_attachment=True)
        return self.render_template('reports.html')

class CsMonthView(BaseView):
    default_view = 'csmonthly'
    @expose('/csmonthly', methods=['POST', 'GET'])
    def csmonthly(self):
        print('csmonthly')
        #print(request.submit.value)
        if request.method == 'POST':
            print('post')
            print('POST', request.data) 
        #report_url(self)
        return self.render_template('csmonthly.html')
    
    @expose('/csmonthly_rep/', methods=['POST', 'GET'])
    def csmonthly_rep(self):
        print('csmonthly_rep')
        #print(request.submit.value)
        if request.method == 'POST':        
            print('csmonthly_rep')
            print('csmonthly_rep')
            ws = report_all()
            return send_file(ws, as_attachment=True)
        return self.render_template('reports.html')

class CurrentCommentView(ModelView):
    datamodel = SQLAInterface(Comments)
    search_columns = ['included','closed', 'document','revision']
    base_order = ('id_c','asc')
    order_columns = ['id_c']
    label_columns = {
        'pretty_style' : 'Type',
        'pretty_included': 'Included',
        'pretty_closed': 'Closed',
        'document': 'Bapco Code',
        'pretty_comment': 'Comments',
        'pretty_reply': 'Replies',
        'pretty_revision': 'Rev',
    }
    #list_columns = ['document','id_c','pretty_partner','pretty_revision','page', 'author','pretty_style', 'pretty_comment', 'pretty_reply', 'pretty_included','pretty_closed']
    list_columns = ['pretty_style', 'comment', 'pretty_reply', 'pretty_included','pretty_closed']
    base_filters = [['revision.current', FilterEqual, 1]]

    #base_permissions = ['can_list', 'can_edit']
    #list_widget = ListThumbnail
     
    add_exclude_columns = ['created_on', 'changed_on']
    edit_exclude_columns = ['created_on', 'changed_on']
    show_exclude_columns = ['comments']
    
    
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
    
    @has_access
    @permission_name('documentview')
    @action("include", "Include AND Close All", "Iclude and Close all Comments, Really?", "fa-rocket")
    def include(self, items):
        if isinstance(items, list):
            for item in items:

                item.closed = True
                item.included = True

                check_doc_closed(item.document_id)
                action_include_close(item)

                self.datamodel.edit(item)

            self.update_redirect()

        else:
            # do not seem to ever came here....
            item = items
            
            item.closed = True
            item.included = True

            action_include_close(item)
            check_doc_closed(item.document_id) 

            self.datamodel.edit(item)
            self.update_redirect()

        return redirect(self.get_redirect())
    
    @has_access
    @permission_name('documentview')
    @action("close", "Close All", "Close all Comments, Really?", "fa-rocket")
    def close(self, items):
        if isinstance(items, list):
            for item in items:
                item.closed = True
                
                check_doc_closed(item.document_id) # for every items?
                action_close(item)
                self.datamodel.edit(item)
            self.update_redirect()
        else:
            # do not seem to ever came here....
            item = items
            
            item.closed = True
            
            self.datamodel.edit(item)
            check_doc_closed(item.document_id)
            self.update_redirect()
        return redirect(self.get_redirect())


    #def post_update(self, item):
        #check_doc_closed(item.document_id)
    

class CommentView(ModelView):
    datamodel = SQLAInterface(Comments)
    search_columns = ['included','closed', 'document','revision']
    base_order = ('id_c','asc')
    order_columns = ['id_c']
    label_columns = {
        'pretty_style' : 'Type',
        'pretty_included': 'Included',
        'pretty_closed': 'Closed',
        'document': 'Bapco Code',
        'pretty_comment': 'Comments',
        'pretty_reply': 'Replies',
        'pretty_revision': 'Rev',
    }
    #list_columns = ['document','id_c','pretty_partner','pretty_revision','page', 'author','pretty_style', 'pretty_comment', 'pretty_reply', 'pretty_included','pretty_closed']
    list_columns = ['pretty_style', 'pretty_comment', 'pretty_reply', 'pretty_included','pretty_closed']
    #base_filters = [['revision.current', FilterEqual, 1]]

    #base_permissions = ['can_list', 'can_edit']
    #list_widget = ListThumbnail
     
    add_exclude_columns = ['created_on', 'changed_on']
    edit_exclude_columns = ['created_on', 'changed_on','created_by', 'changed_by', 'partner','document','id_c','style','note','type_reply']
    show_exclude_columns = ['comments','partner']
    

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
    
    #@has_access
    @action("include", "Include All", "Iclude all Really?", "fa-rocket")
    def include(self, items):
        if isinstance(items, list):
            for item in items:
                item.closed = True
                item.included = True
                self.datamodel.edit(item)
            self.update_redirect()
        else:
            items.closed = True
            items.included = True
            self.datamodel.edit(item)
        return redirect(self.get_redirect())
    def post_update(self, item):
        check_doc_closed(item.document_id)
    
'''
class OpenCommentsView(ModelView):
    datamodel = SQLAInterface(Comments)

    base_filters = [['type_reply', FilterEqual, True],
                    ['closed', FilterEqual, False]
    
    ]
'''
class RevisionChart(GroupByChartView):
    datamodel = SQLAInterface(Comments)
    #chart_type = 'PieChart'
    #height = 500
    chart_title = 'Revisiom Comments By Status'
    #search_columns = ['type_reply', 'included', 'closed','style']
    #base_filters = [['type_reply', FilterEqual, True],['closed', FilterEqual, False]]
    definitions = [
        
        
        {
            'label': 'Document',
            'group': 'doc',
            'series': [
                (aggregate_count, 'comment'),
                
                (aggregate_sum, 'included'),
                (aggregate_sum, 'closed'),
                #(aggregate_count, 'open_comments')             
            ]
        }
        ]

class CommentsChart(GroupByChartView):
    datamodel = SQLAInterface(Comments)
    chart_type = 'BarChart'
    #height = '2000px'
    chart_title = 'Open CS Chart'
    search_columns = ['type_reply', 'included', 'closed','style']
    #base_filters = [['type_reply', FilterEqual, True],['closed', FilterEqual, False]]
    definitions = [
        
        {
            'label': 'Author',
            'group': 'author',
            'series': [
                (aggregate_count, 'comment'),
                (aggregate_sum, 'closed'),
                #(aggregate_sum, 'included')             
            ]
        },
        
        {
            'label': 'Document',
            'group': 'doc',
            'series': [
                (aggregate_count, 'comment'),
                (aggregate_sum, 'closed'),
                #(aggregate_sum, 'included'),
                #(aggregate_count, 'open_comments')             
            ]
        }
        ]

class CommentsPieChart(GroupByChartView):
    datamodel = SQLAInterface(Comments)
    chart_type = 'PieChart'
    definitions = [
       
        {
            'label': 'Closed',
            'group': 'closed',
            'series': [(aggregate_count, 'closed')]
        },
        {
            'label': 'Included',
            'group': 'included',
            'series': [(aggregate_count, 'included')]
        }
        ]

class DocRevisionList(ModelView):
    datamodel = SQLAInterface(Revisions)
    related_views = [CommentView]
    
    show_template = 'appbuilder/general/model/show_cascade.html'
    list_title = 'All CS Revisions'
    base_permissions = ['can_list','can_show','can_edit']
    order_columns = ['pos']
    list_columns = ['pretty_revision','trasmittal', 'pretty_date_trs','action_code', 'note', 'download']
    #list_widget = ListBlock
    edit_columns = ['revision', 'trasmittal', 'date_trs','action_code','revision_type', 'note']
    show_columns = ['pretty_doc_revision','file', 'revision', 'trasmittal', 'date_trs','note','action_code']
    label_columns = {
        
        'action_code': 'Response Code',
        
        'pretty_revision': 'Rev.',
        'pretty_doc_revision': 'Document',
        'pretty_date': 'Date',
        'pretty_date_trs': 'Trans. Date',
        'download': 'File',
        'trasmittal': 'Transmittal'
    }

    #@has_access
    #@permission_name('revisionview')
    @action("current", "Current Revision", "Set This Revision as Current?", "fa-rocket")
    def current(self, item):
        item = item[0]
        print('file in item[0]', item.file)
        item.document_id, item.partner = check_Doc(self, item) 
        set_current(self, item)
        self.update_redirect()
        return redirect(self.get_redirect())
    
    
     
class RevisionList(ModelView):
    datamodel = SQLAInterface(Revisions)
    base_permissions = ['can_this_form_post','can_list', 'can_show']


    search_columns = ['document','revision','reply', 'trasmittal','date_trs']
    label_columns = {
        'document': 'Bapco Code',
        'action_code': 'Response Code',
        'document.code': 'Bapco Code',
        'pretty_revision': 'Rev.',
        'pretty_doc_revision': 'Document',
        'pretty_date': 'Date',
        'pretty_date_trs': 'Trans. Date',
        'download': 'File',
        'trasmittal': 'Transmittal'
    }
    list_columns = ['pos','pretty_revision','trasmittal', 'pretty_date_trs','action_code', 'note', 'download']
    #list_columns = ['document','pretty_revision','download']
    #list_widget = ListThumbnail
    add_exclude_columns = ['created_on', 'changed_on']
    edit_exclude_columns = ['created_on', 'changed_on']
    edit_columns = ['pos', 'revision','trasmittal','date_trs', 'action_code', 'note']
    add_columns = ['file', 'revision', 'trasmittal', 'date_trs','action_code', 'note']
    show_exclude_columns = ['comments']
    base_order = ('pos','asc')
    
    order_columns = ['document','created_on','changed_on']
    related_views = [CommentView]
    show_template = 'appbuilder/general/model/show_cascade.html'
    show_fieldsets = [
                        (
                            'Revision Info',
                            {'fields': ['document.code', 'revision', 'trasmittal', 'date_trs','action_code', 'note']}
                        ),
                        (
                            'Revision Audit',
                            {'fields': ['created_on',
                                        'created_by',
                                        'changed_on',
                                        'changed_by'], 'expanded':False}
                        ),
                     ]

    

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
    '''
    @action("check_Rev", "Check Last Rev", "Check all Really?", "fa-rocket")
    def chec_rev(self, item):
        last_rev(self, item)
        self.update_redirect()
        return redirect(self.get_redirect())
    '''
    @action("current", "Current Revision", "Set This Revision as Current?", "fa-rocket")
    def current(self, item):
        item = item[0]
        print('file in item[0]', item.file)
        item.document_id, item.partner = check_Doc(self, item) 
        set_current(self, item)
        self.update_redirect()
        return redirect(self.get_redirect())

    def pre_add(self,item):
            
        print('from views, pre_add function')
        
        item.reply = check_reply(self, item)
        item.document_id, item.partner = check_Doc(self, item)
        
        filename = get_file_original_name(item.file)
        result, message = precheck_doc(self,item)
        if result == False:
            print('precheck_doc finction')
            #return self.render_template('fileinfo.html', param=message)
            #flash(message, category='warning')
            
            return abort(400, message)
        

    def post_add(self, item):
        
        print('post add functions on revision')
        
        comments(item)
        check_doc_closed(item.document_id)

class RevisionFileChange(ModelView):
    datamodel = SQLAInterface(Revisions)
    search_columns = ['document','revision','reply', 'trasmittal','date_trs', 'action_code']
    label_columns = {
        'document': 'Bapco Code',
        'action_code': 'Response Code',
        'document.code': 'Bapco Code',
        'pretty_revision': 'Rev.',
        'pretty_doc_revision': 'Document',
        'pretty_date': 'Date',
        'pretty_date_trs': 'Trans. Date',
        'download': 'File',
        'trasmittal': 'Transmittal'
    }
    list_columns = ['document.code', 'pretty_revision','trasmittal', 'pretty_date_trs','action_code', 'note', 'download']
    #list_columns = ['document','pretty_revision','download']
    #list_widget = ListThumbnail
    base_permissions = ['can_edit', 'can_list']
    add_exclude_columns = ['created_on', 'changed_on']
    edit_exclude_columns = ['created_on', 'changed_on']
    edit_columns = ['file', 'reply']
    add_columns = ['file', 'revision', 'trasmittal', 'date_trs','action_code', 'note']
    show_exclude_columns = ['comments']
    base_order = ('document.code', 'asc')
    
    order_columns = ['document','created_on','changed_on']
    related_views = [CommentView]
    show_template = 'appbuilder/general/model/show_cascade.html'
    show_fieldsets = [
                        (
                            'Revision Info',
                            {'fields': ['document.code', 'revision', 'trasmittal', 'date_trs','action_code', 'note']}
                        ),
                        (
                            'Revision Audit',
                            {'fields': ['created_on',
                                        'created_by',
                                        'changed_on',
                                        'changed_by'], 'expanded':False}
                        ),
                     ]

    def pre_add(self,item):
            
        print('from views, pre_add function')
        
        item.reply = check_reply(self, item)
        item.document_id, item.partner = check_Doc(self, item)
        
        filename = get_file_original_name(item.file)
        result, message = precheck_doc(self,item)
        if result == False:
            print('precheck_doc finction')
            #return self.render_template('fileinfo.html', param=message)
            #flash(message, category='warning')
            
            return abort(400, message)
        

    def post_add(self, item):
        
        print('post add functions on revision')

        comments(item)
        check_doc_closed(item.document_id)

class MyRevisionsList(ModelView):
    
    datamodel = SQLAInterface(Revisions)
    list_title = 'My Revisions List'
    search_columns = ['document','revision','reply', 'trasmittal','date_trs']
    label_columns = {
        'document': 'Bapco Code',
        'action_code': 'Response Code',
        'document.code': 'Bapco Code',
        'pretty_revision': 'Rev.',
        'pretty_doc_revision': 'Document',
        'pretty_date': 'Date',
        'pretty_date_trs': 'Trans. Date',
        'download': 'File',
        'trasmittal': 'Transmittal'
    }
    list_columns = ['document.code','pretty_revision','trasmittal', 'pretty_date_trs','action_code', 'note','changed_on', 'download']
    base_filters = [['created_by', FilterEqualFunction, get_user]]
    #list_columns = ['document','pretty_revision','download']
    #list_widget = ListThumbnail
    add_exclude_columns = ['created_on', 'changed_on']
    edit_exclude_columns = ['created_on', 'changed_on']
    edit_columns = ['pos', 'revision','trasmittal','date_trs', 'action_code', 'note']
    add_columns = ['file', 'revision', 'trasmittal', 'date_trs','action_code', 'note']
    show_exclude_columns = ['comments']
    base_order = ('pos','asc')
    
    order_columns = ['document','created_on','changed_on']
    related_views = [CommentView]
    show_template = 'appbuilder/general/model/show_cascade.html'
    show_fieldsets = [
                        (
                            'Revision Info',
                            {'fields': ['document.code', 'revision', 'trasmittal', 'date_trs','action_code', 'note']}
                        ),
                        (
                            'Revision Audit',
                            {'fields': ['created_on',
                                        'created_by',
                                        'changed_on',
                                        'changed_by'], 'expanded':False}
                        ),
                     ]

    

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
    '''
    @action("check_Rev", "Check Last Rev", "Check all Really?", "fa-rocket")
    def chec_rev(self, item):
        last_rev(self, item)
        self.update_redirect()
        return redirect(self.get_redirect())
    '''
    @action("current", "Current Revision", "Set This Revision as Current?", "fa-rocket")
    def current(self, item):
        item = item[0]
        item.document_id, item.partner = check_Doc(self, item) 
        set_current(self, item)
        self.update_redirect()
        return redirect(self.get_redirect())

    def pre_add(self,item):
            
        print('from views, pre_add function')
        
        item.reply = check_reply(self, item)
        item.document_id, item.partner = check_Doc(self, item)
        
        filename = get_file_original_name(item.file)
        result, message = precheck_doc(self,item)
        if result == False:
            print('precheck_doc finction')
            #return self.render_template('fileinfo.html', param=message)
            #flash(message, category='warning')
            
            return abort(400, message)

class RevisionView(ModelView):
    datamodel = SQLAInterface(Revisions)
    search_columns = ['document','revision','reply', 'trasmittal','date_trs','action_code', 'note']
    label_columns = {
        'document': 'Bapco Code',
        'action_code': 'Bapco Response Code',
        'document.code': 'Bapco Code',
        'pretty_revision': 'Rev.',
        'pretty_doc_revision': 'Document',
        'pretty_date': 'Date',
        'pretty_date_trs': 'Trans. Date',
        'download': 'File',
        'trasmittal': 'Transmittal'
    }
    
    base_filters = [['trasmittal', FilterNotContains, "%SOC%"],
                    ['trasmittal', FilterNotContains, "%MOC%"]]
    
    list_columns = ['document.code', 'pretty_revision','trasmittal', 'pretty_date_trs','action_code', 'note', 'download']
    #list_columns = ['document','pretty_revision','download']
    #list_widget = ListThumbnail
    add_exclude_columns = ['created_on', 'changed_on']
    edit_exclude_columns = ['created_on', 'changed_on']
    edit_columns = ['trasmittal', 'revision','date_trs', 'action_code', 'note']
    add_columns = ['file', 'revision', 'trasmittal', 'date_trs','action_code', 'note']
    show_exclude_columns = ['comments']
    base_order = ('document.code','asc')
    
    order_columns = ['document','created_on','changed_on']
    related_views = [CommentView]
    show_template = 'appbuilder/general/model/show_cascade.html'
    show_fieldsets = [
                        (
                            'Revision Info',
                            {'fields': ['document.code', 'revision', 'trasmittal', 'date_trs','action_code', 'note']}
                        ),
                        (
                            'Revision Audit',
                            {'fields': ['created_on',
                                        'created_by',
                                        'changed_on',
                                        'changed_by'], 'expanded':False}
                        ),
                     ]

    

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

    def pre_add(self,item):
            
        print('from views, pre_add function')
        
        item.reply = check_reply(self, item)
        item.document_id, item.partner = check_Doc(self, item)
        session['last_document'] = item.document_id
        print('last document ----', session['last_document'])
        filename = get_file_original_name(item.file)
        result, message = precheck_doc(self,item)
        if result == False:
            print('precheck_doc finction')
            #return self.render_template('fileinfo.html', param=message)
            #flash(message, category='warning')
            
            return abort(400, message)
        

    def post_add(self, item):
        
        print('post add functions on revision')

        comments(item)
        check_doc_closed(item.document_id)
        

       
    def post_add_redirect(self):
        """Override this function to control the redirect after add endpoint is called."""
        
        doc = str(session['last_document'])

        return redirect(url_for('DocumentView.show', pk=doc))

class UploadCommentsView(ModelView):
    datamodel = SQLAInterface(Revisions)
    default_view = 'add'
    base_permissions = ['can_add',]
    add_columns = ['file','revision_type', 'revision', 'trasmittal', 'date_trs','action_code', 'note']
    
    def pre_add(self,item):

        item.reply = check_reply(self, item)
        item.document_id, item.partner = check_Doc(self, item)
        
        session['last_document'] = item.document_id
        
        filename = get_file_original_name(item.file)
        result, message = precheck_doc(self,item)
        
        if result == False:
            
            return abort(400, message)
        

    def post_add(self, item):

        comments(item)
        check_doc_closed(item.document_id)
        

       
    def post_add_redirect(self):
        """Override this function to control the redirect after add endpoint is called."""
        
        doc = str(session['last_document'])

        return redirect(url_for('DocumentView.show', pk=doc))


class DocumentView(ModelView):
    datamodel = SQLAInterface(Document)
    related_views = [CurrentCommentView, DocRevisionList] 
    
    #list_template = 'appbuilder/general/model/multiple_views.html'
    show_template = 'appbuilder/general/model/show_cascade.html'
    show_widget = ShowDocument
    

    add_exclude_columns = ['created_on', 'changed_on','comments']
    edit_exclude_columns = ['created_on', 'changed_on','comments']
    show_exclude_columns = ['comments']
    search_exclude_columns = ['created_on', 'changed_on']
    search_columns = ['partner', 'code' ]

    base_filters = [['partner', FilterNotContains, "SOC"],
                    ['partner', FilterNotContains, "MOC"]]
    base_permissions = ['can_this_form_post','can_list', 'can_show']
    label_columns = {
        'code': 'Document',
        'count': 'Tot',
        'count_included': 'Included',
        'count_closed': 'Closed',
        'count_open': 'Open',
        'count_no_reply': "No Reply",
    }
    list_columns = ['code','partner', 'revision', 'count', 'count_included' ,'count_closed']
    show_fieldsets = [
                        (
                            'Document Info',
                            {'fields': ['code', 'revision',
    
                                        'changed_on',
                                        'changed_by']}
                        ),
                     
                     ]

    
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

class DocumentListView(ModelView):
    datamodel = SQLAInterface(Document)
    search_widget = [SearchWidget]
    search_columns = ['code','unit','materialclass','doctype']
    #search_exclude_columns = ['created_by']
    #list_widget = ListBlock
    
    list_columns = ['code','unit','materialclass','doctype']

class DocumentMonitorView(MultipleView, ModelView):
    datamodel = SQLAInterface(Document)
    views = [CommentsChart, DocumentView, RevisionChart]
    

class SuperDocumentView(ModelView):
    datamodel = SQLAInterface(Document)
    related_views = [CommentView, RevisionList]
    show_template = 'appbuilder/general/model/show_cascade.html'

    add_exclude_columns = ['created_on', 'changed_on','comments']
    edit_exclude_columns = ['created_on', 'changed_on','comments']
    show_exclude_columns = ['comments']
    search_exclude_columns = ['created_on', 'changed_on']
    search_columns = ['partner', 'code' ]
    

    label_columns = {
        'code': 'Bapco Code',
        'count': 'Tot',
        'count_included': 'Included',
        'count_closed': 'Closed',
        'count_open': 'Open',
        'count_no_reply': "No Reply",
    }
    list_columns = ['code','partner', 'revision', 'count', 'count_included' ,'count_closed']
    show_fieldsets = [
                        (
                            'Document Info',
                            {'fields': ['code', 'revision', 'partner']}
                        ),
                        (
                            'Document Audit',
                            {'fields': ['created_on',
                                        'created_by',
                                        'changed_on',
                                        'changed_by'], 'expanded':False}
                        ),
                     ]

    
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
    '''
    @action("check", "Check", "Check all Really?", "fa-rocket")
    def check(self, items):
        if isinstance(items, list):
            for item in items:
                test_closed(item.id)
            self.update_redirect()
        else:
            test_closed(items.id)
        return redirect(self.get_redirect())
    
    @action("check_Rev", "Check Rev", "Check all Really?", "fa-rocket")
    def chec_rev(self, item):
        last_rev(self, item)
        return redirect(self.get_redirect())
    '''


class RevisionTypeView(ModelView):
    datamodel = SQLAInterface(Revision_type)
    list_columns = ['name']
    edit_columns = ['name']
    add_columns = ['name'] 


"""
    Application wide 404 error handler
"""
 
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404##


       
        
#db.create_all()
from mass_update import mass_update
#appbuilder.security_cleanup()
appbuilder.add_view(RevisionTypeView,'Revision Type',icon="fas fa-file-pdf", category="Setting", category_icon='fas fa-file-alt')

#appbuilder.add_view(UploadComments,'Upload Comments',icon="fa-folder-open-o", category="My Category", category_icon='fas fa-comment')
#appbuilder.add_view(Report,'Reports',icon="fas fa-file-excel", category="Dashboard", category_icon='fas fa-tachometer-alt')
#appbuilder.add_view(CsRepliesView,'CS Replies Status',icon="fas fa-file-excel", category="Dashboard", category_icon='fas fa-tachometer-alt')
#appbuilder.add_view(CsMonthView,'CS Status by Month',icon="fas fa-file-excel", category="Dashboard", category_icon='fas fa-tachometer-alt')
appbuilder.add_view(CsDashboardView,'CS General Dasboard',icon="fas fa-chart-bar", category="Dashboard", category_icon='fas fa-tachometer-alt')
appbuilder.add_view(CsTimeDashView,'CS Time Dasboard',icon="fas fa-chart-bar", category="Dashboard", category_icon='fas fa-tachometer-alt')

appbuilder.add_view(DocumentView,'Document List',icon="fas fa-file-pdf", category="Document", category_icon='fas fa-file-alt')

appbuilder.add_view(UploadCommentsView,'Upload Comments',icon="fas fa-upload", category="Comments", category_icon='fas fa-comment')
appbuilder.add_separator(category='Comments')
appbuilder.add_view(MyRevisionsList,'My CS File List',icon="fas fa-sort-amount-up", category="Comments", category_icon='fas fa-comment')
appbuilder.add_view(RevisionFileChange,'Revision File Change',icon="fas fa-exchange-alt", category="Comments", category_icon='fas fa-comment')
appbuilder.add_separator(category='Comments')
appbuilder.add_view(RevisionView,'All CS File List',icon="fas fa-list-ul", category="Comments", category_icon='fas fa-comment')

#appbuilder.add_view(DocumentMonitorView,'Document Monitor',icon="fas fa-file-pdf", category="Comments", category_icon='fas fa-comment')

#appbuilder.add_view(SuperDocumentView,'SuperDocument',icon="fas fa-file-pdf", category="Document", category_icon='fas fa-file')

appbuilder.add_view_no_menu(RevisionList)
appbuilder.add_view_no_menu(DocRevisionList) 
appbuilder.add_view_no_menu(DocumentListView) 
appbuilder.add_view_no_menu(RevisionChart) 
appbuilder.add_view_no_menu(CommentView) 
appbuilder.add_view_no_menu(CurrentCommentView)
#appbuilder.add_view(CommentView,'Comments',icon="fas fa-comments", category="Comments", category_icon='fas fa-comment')

#appbuilder.add_view(CommentsChart,'Comment Chart',icon="fas fa-code-branch", category="Statistics", category_icon='fas fa-comment')
#appbuilder.add_view(CommentsPieChart,'Comment Pie Chart',icon="fas fa-code-branch", category="Statistics", category_icon='fas fa-comment')

#
#set_position()   
#mass_update()  
#set_comments_blank()
#set_comments_included()
#transmittall()
 
#check_duplicates()
#reply_rev()

#find_action()
#check_doc_closed2() 
