//  @@@ web_export_view custom JS @@@
//#############################################################################
//    
//    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
//    Copyright (C) 2012 Therp BV (<http://therp.nl>)
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU Affero General Public License as published
//    by the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU Affero General Public License for more details.
//
//    You should have received a copy of the GNU Affero General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//#############################################################################
openerp.web_export_view = function(instance, m) {

    var _t = instance.web._t,
    QWeb = instance.web.qweb;
    flg=true;
    curr_data={}
    export_columns_keys = [];
    export_columns_names = [];
    export_rows = [];
    check_count=0;
    data_count=0;
    instance.web.Sidebar.include({
        redraw: function() {
            var self = this;
            this._super.apply(this, arguments);
            //self.$el.find('.oe_sidebar').append(QWeb.render('AddExportViewMain', {widget: self}));
//            self.$el.find('.oe_bold oe_list_button_import_excel oe_form_button').on('click', self.on_sidebar_export_view_xls);
//            var links = document.getElementsByClassName("oe_list_button_import_excel");
//            if (links && links[0]){
//                links[0].onclick = function() {
//                    self.on_sidebar_export_view_xls();
//                };
//            }
//            self.$el.find('.oe_bold oe_list_button_import_excel_outward oe_form_button').on('click', self.on_sidebar_export_view_xls_outward);
//            var links_outward = document.getElementsByClassName("oe_list_button_import_excel_outward");
//            if (links_outward && links_outward[0]){
//                links_outward[0].onclick = function() {
//                    self.on_sidebar_export_view_xls_outward();
//                };
//            }            
//            self.$el.find('.oe_bold oe_list_button_import_excel_casesheet oe_form_button').on('click', self.on_sidebar_export_view_xls_casesheet);
//            var links_casesheet = document.getElementsByClassName("oe_list_button_import_excel_casesheet");            
//            if (links_casesheet && links_casesheet[0]){
//                links_casesheet[0].onclick = function() {
//                    self.on_sidebar_export_view_xls_casesheet();
//                };
//            }
            self.$el.find('oe_bold oe_list_button_import_excel_court_diary oe_form_button').on('click', self.on_sidebar_export_view_xls_court_proceedings);
            var links_casesheet = document.getElementsByClassName("oe_list_button_import_excel_court_diary");            
            if (links_casesheet && links_casesheet[0]){
                links_casesheet[0].onclick = function() {
                    self.on_sidebar_export_view_xls_court_proceedings();
                };
            }
            self.$el.find('oe_bold oe_list_button_import_excel_cases_bills_info oe_form_button').on('click', self.on_sidebar_export_view_xls_cases_bills_info);
            var links_case_bill = document.getElementsByClassName("oe_list_button_import_excel_cases_bills_info");            
            if (links_case_bill && links_case_bill[0]){
                links_case_bill[0].onclick = function() {
                    self.on_sidebar_export_view_xls_cases_bills_info();
                };
            }
        },
//	fetchval: function(id_val){
//	 //retval = new instance.web.Model("inward.register").call('write', [[parseInt(id_val)], {'exported':true}]);
//	 return new instance.web.Model("inward.register").get_func("read")(parseInt(id_val), [])
//	},
//	fetchval_outward: function(id_val){
//	 //retval = new instance.web.Model("inward.register").call('write', [[parseInt(id_val)], {'exported':true}]);
//	 return new instance.web.Model("outward.register").get_func("read")(parseInt(id_val), [])
//	},
//	fetchval_casesheet: function(id_val){
//	 //retval = new instance.web.Model("inward.register").call('write', [[parseInt(id_val)], {'exported':true}]);
//	 return new instance.web.Model("case.sheet").get_func("read")(parseInt(id_val), [], {'exported':true})
//	},
	fetchval_proceedings: function(id_val){
	 return new instance.web.Model("court.proceedings").get_func("read")(parseInt(id_val), [])
	},
	fetchval_proceedings_ids: function(){
	 return new instance.web.Model("court.diary").get_func("get_ids")()
	},
	fetchval_case_bills_report: function(id_val){
	 return new instance.web.Model("case.bills.details").get_func("read")(parseInt(id_val), [])
	},
	fetchval_case_bills_report_ids: function(){
	 return new instance.web.Model("cases.bills.info").get_func("get_ids")()
	},
        on_sidebar_export_view_xls: function() {
            flg=true;
	    curr_data={}
	    export_columns_keys = [];
	    export_columns_names = [];
	    export_rows = [];
	    check_count=0;
	    data_count=0;
            // Select the first list of the current (form) view
            // or assume the main view is a list view and use that
            var self = this,
            view = this.getParent(),
            children = view.getChildren();
           
            if (children) {
                children.every(function(child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false; // break out of the loop
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false; // break out of the loop
                    }
                    return true;
                });
            }
           
            start: 
           /* $.each(view.visible_columns, function(){
            
                if(this.tag=='field'){                	
                    // non-fields like `_group` or buttons
                    export_columns_keys.push(this.id);                    
                    export_columns_names.push(this.string);
                }
            });*/
            var column_keys = ['name','date','file_number','agency_from','addressee_name','assignee_id'];
            var column_names = ['Entry Number','Entry Date','File Number','Agency From','Given To','Assignee'];
            for(i=0;i<column_keys.length;i++)
            {
            	export_columns_keys.push(column_keys[i]);                    
            	export_columns_names.push(column_names[i]);
            }
            //export_columns_keys.push('categ_id');                    
            //export_columns_names.push('Category ID');
            rows = view.$el.find('.oe_list_content > tbody > tr');
            
            //var Model = new instance.web.Model('res.users');
            check_count = $('input[name="radiogroup"]:checked').length;
            total_rows = $('input[name="radiogroup"]').length;
            if(check_count<=0)
            {
            	alert('Please Select record(s) to Export');
            	return;
            }
            else
            {
            	//for(cnt=0;cnt<total_rows;cnt++)
            	{
            		
            	}
            }
            $('.oe_list_content tr').each(function (i, row) {
	
        // reference all the stuff you need first
         $row = $(row),
         //       $row = $(this);
                flg=true;                
                // find only rows with data
                if($row.attr('data-id')){
              
                    export_row = [];
                    
                    checked = $row.find('th input[type=checkbox]').attr("checked");                    
                    
                    
                    if (checked === "checked"){
                   
            	 
            	 	var curr_data_obj = self.fetchval($row.attr('data-id')).then(function(res){curr_data = res;flg=false;self.loop_data(export_columns_keys,curr_data,"Export Inward Register");});
            	 
                //Model.call('write', [[$row.attr('data-id')], {'price_extra':50}]);
 /*               
start: while(true) {
  if(flg==true) continue start;
  break;
}*/

                 
                     
                        //alert(export_rows);
                        //export_rows.push(export_row);
                        
                     
                    }
                   
                }
                
            });
           
        },
        on_sidebar_export_view_xls_outward: function() {
            flg=true;
	    curr_data={}
	    export_columns_keys = [];
	    export_columns_names = [];
	    export_rows = [];
	    check_count=0;
	    data_count=0;
            // Select the first list of the current (form) view
            // or assume the main view is a list view and use that
            var self = this,
            view = this.getParent(),
            children = view.getChildren();
           
            if (children) {
                children.every(function(child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false; // break out of the loop
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false; // break out of the loop
                    }
                    return true;
                });
            }
           
            start: 
           /* $.each(view.visible_columns, function(){
            
                if(this.tag=='field'){                	
                    // non-fields like `_group` or buttons
                    export_columns_keys.push(this.id);                    
                    export_columns_names.push(this.string);
                }
            });*/
            var column_keys = ['name','date','file_number','to_name_acknowledge'];
            var column_names = ['Entry Number','Entry Date','File Number','To Name - Acknowledgement'];
            for(i=0;i<column_keys.length;i++)
            {
            	export_columns_keys.push(column_keys[i]);                    
            	export_columns_names.push(column_names[i]);
            }
            //export_columns_keys.push('categ_id');                    
            //export_columns_names.push('Category ID');
            rows = view.$el.find('.oe_list_content > tbody > tr');
            
            //var Model = new instance.web.Model('res.users');
            check_count = $('input[name="radiogroup"]:checked').length;
            total_rows = $('input[name="radiogroup"]').length;
            if(check_count<=0)
            {
            	alert('Please Select record(s) to Export');
            	return;
            }
            else
            {
            	//for(cnt=0;cnt<total_rows;cnt++)
            	{
            		
            	}
            }
            $('.oe_list_content tr').each(function (i, row) {
	
        // reference all the stuff you need first
         $row = $(row),
         //       $row = $(this);
                flg=true;                
                // find only rows with data
                if($row.attr('data-id')){
              
                    export_row = [];
                    
                    checked = $row.find('th input[type=checkbox]').attr("checked");                    
                    
                    
                    if (checked === "checked"){
                   
            	 
            	 	var curr_data_obj = self.fetchval_outward($row.attr('data-id')).then(function(res){curr_data = res;flg=false;self.loop_data(export_columns_keys,curr_data,"Export Outward Register");});
            	 
                //Model.call('write', [[$row.attr('data-id')], {'price_extra':50}]);
 /*               
start: while(true) {
  if(flg==true) continue start;
  break;
}*/
                        //alert(export_rows);
                        //export_rows.push(export_row);
                        
                     
                    }
                   
                }
                
            });
        },
        on_sidebar_export_view_xls_casesheet: function() {
            flg=true;
	    curr_data={}
	    export_columns_keys = [];
	    export_columns_names = [];
	    export_rows = [];
	    check_count=0;
	    data_count=0;
            // Select the first list of the current (form) view
            // or assume the main view is a list view and use that
            var self = this,
            view = this.getParent(),
            children = view.getChildren();
           
            if (children) {
                children.every(function(child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false; // break out of the loop
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false; // break out of the loop
                    }
                    return true;
                });
            }
           
            start: 
           /* $.each(view.visible_columns, function(){
            
                if(this.tag=='field'){                	
                    // non-fields like `_group` or buttons
                    export_columns_keys.push(this.id);                    
                    export_columns_names.push(this.string);
                }
            });*/
            var column_keys = ['name','date','casetype_id','work_type', 'client_id','assignee_id','division_id','bill_type','fixed_price'];
            var column_names = ['File Number','File Date','Case Type','Type of Work','Client Name','Assignee','Department/Division','Billing Type','Billing Amount'];
            for(i=0;i<column_keys.length;i++)
            {
            	export_columns_keys.push(column_keys[i]);                    
            	export_columns_names.push(column_names[i]);
            }
            //export_columns_keys.push('categ_id');                    
            //export_columns_names.push('Category ID');
            rows = view.$el.find('.oe_list_content > tbody > tr');
            
            //var Model = new instance.web.Model('res.users');
            check_count = $('input[name="radiogroup"]:checked').length;
            total_rows = $('input[name="radiogroup"]').length;
            if(check_count<=0)
            {
            	alert('Please Select record(s) to Export');
            	return;
            }
            else
            {
            	//for(cnt=0;cnt<total_rows;cnt++)
            	{
            		
            	}
            }
            $('.oe_list_content tr').each(function (i, row) {
	
        // reference all the stuff you need first
         $row = $(row),
         //       $row = $(this);
                flg=true;                
                // find only rows with data
                if($row.attr('data-id')){
              
                    export_row = [];
                    
                    checked = $row.find('th input[type=checkbox]').attr("checked");                    
                    
                    
                    if (checked === "checked"){
                   
            	 
            	 	var curr_data_obj = self.fetchval_casesheet($row.attr('data-id')).then(function(res){curr_data = res;flg=false;self.loop_data(export_columns_keys,curr_data,"Export Case Sheet Details");});
            	 
                //Model.call('write', [[$row.attr('data-id')], {'price_extra':50}]);
 /*               
start: while(true) {
  if(flg==true) continue start;
  break;
}*/
                        //alert(export_rows);
                        //export_rows.push(export_row);
                        
                     
                    }
                   
                }
                
            });
        },
        on_sidebar_export_view_xls_court_proceedings: function() {
	    
            flg=true;
	    curr_data={}
	    export_columns_keys = [];
	    export_columns_names = [];
	    export_rows = [];
	    check_count=0;
	    data_count=0;
            // Select the first list of the current (form) view
            // or assume the main view is a list view and use that
            var self = this,
            view = this.getParent(),
            children = view.getChildren();
           
            if (children) {
                children.every(function(child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false; // break out of the loop
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false; // break out of the loop
                    }
                    return true;
                });
            }
           
            start: 
           /* $.each(view.visible_columns, function(){
            
                if(this.tag=='field'){                	
                    // non-fields like `_group` or buttons
                    export_columns_keys.push(this.id);                    
                    export_columns_names.push(this.string);
                }
            });*/
            var column_keys = ['case_id','client_id','proceed_date','name','billable','effective','flg_next_date','next_proceed_date','stage_id'];
            var column_names = ['File Number','Client','Proceed Date','Remarks','Billable','Effective','Next Date?','Next Proceed Date', 'Stage'];
            for(i=0;i<column_keys.length;i++)
            {
            	export_columns_keys.push(column_keys[i]);                    
            	export_columns_names.push(column_names[i]);
            }
            var listids;
            var curr_data_obj1 = self.fetchval_proceedings_ids().then(function(res){
            listids =res["ids"];
            check_count = listids.length;
            if(check_count<=0)
            {
            	alert('No Court Proceedings to Export');
            	return;
            }
            for(val=0;val<listids.length;val++)
            {
              var curr_data_obj = self.fetchval_proceedings(listids[val]).then(function(res){curr_data = res;flg=false;self.loop_data(export_columns_keys,curr_data,"Export Court Proceedings");});
            }
            });
        },
        on_sidebar_export_view_xls_cases_bills_info: function() {
	    
            flg=true;
	    curr_data={}
	    export_columns_keys = [];
	    export_columns_names = [];
	    export_rows = [];
	    check_count=0;
	    data_count=0;
            // Select the first list of the current (form) view
            // or assume the main view is a list view and use that
            var self = this,
            view = this.getParent(),
            children = view.getChildren();
           
            if (children) {
                children.every(function(child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false; // break out of the loop
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false; // break out of the loop
                    }
                    return true;
                });
            }
           
            start: 
           /* $.each(view.visible_columns, function(){
            
                if(this.tag=='field'){                	
                    // non-fields like `_group` or buttons
                    export_columns_keys.push(this.id);                    
                    export_columns_names.push(this.string);
                }
            });*/
            var column_keys = ['file_no','client_name','first_party','opp_party','assignee','case_no','total_case_amount', 'court_name', 'status', 'legale_number', 'date_invoice', 'amount_total', 'amount_paid', 'amount_balance', 'amount_tds', 'inv_state'];
            var column_names = ['File Number', 'Client Name', 'First Party', 'Opposite Party', 'Assignee', 'Register Number', 'Total Case Amount', 'Court Name', 'Case Status', 'Bill Number', 'Bill Date', 'Bill Amount', 'Amount Paid', 'Balance Amount', 'TDS Amount', 'Bill Status'];
            for(i=0;i<column_keys.length;i++)
            {
            	export_columns_keys.push(column_keys[i]);                    
            	export_columns_names.push(column_names[i]);
            }
            
            var listids;
            var curr_data_obj1 = self.fetchval_case_bills_report_ids().then(function(res){
            listids =res["ids"];
            check_count = listids.length;
            if(check_count<=0)
            {
            	alert('No Case Bills to Export');
            	return;
            }
            for(val=0;val<listids.length;val++)
            {
              var curr_data_obj = self.fetchval_case_bills_report(listids[val]).then(function(res){curr_data = res;flg=false;self.loop_data(export_columns_keys,curr_data,"Case Bills Details");});
            }
            });
        },

        loop_data:function(export_columns_keys_val,curr_data_val,filename){
        export_row = [];
        //alert(export_columns_keys_val);
        //alert(curr_data_val.toSource());
         $.each(export_columns_keys_val,function(){
                            cell = curr_data_val[this];
                            if(typeof cell!='object')
                               export_row.push(cell);
                            else
                               export_row.push(cell[1]);   
                        });
                  export_rows.push(export_row);
                  data_count++;                  
                  if(check_count==data_count)
                  {                  
                  //head_check = $('.oe_list_record_selector:checkbox:checked').length;
		   var self = this;
		    view = this.getParent();
		    
		 $.blockUI();
		    view.session.get_file({
		        url: '/web/export/xls_view',
		        data: {data: JSON.stringify({
		            model : view.model,
		            filename: filename,
		            headers : export_columns_names,
		            rows : export_rows
		        })},
		        complete: $.unblockUI
		    });
            }
        //return export_row;
        return;
        },
    });

};
