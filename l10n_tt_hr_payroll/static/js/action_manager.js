odoo.define('payroll_reports.td4_report', function (require) {
   'use strict';
   var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var utils = require('web.utils');
    var QWeb = core.qweb;
    var _t = core._t;
    var datepicker = require('web.datepicker');
    var time = require('web.time');
   var TD4Reports = AbstractAction.extend({
   console.log('ppppppppppppppp')
   template: 'TD4Report',
       events: {
//                'click #apply_filter': 'apply_filter',
//                'click #pdf': 'print_pdf',
//                'click #xlsx': 'print_xlsx',
//                'click .pl-line': 'show_drop_down',
//                'mousedown div.input-group.date[data-target-input="nearest"]': '_onCalendarIconClick',


       },
       init: function(parent, action) {
             this._super(parent, action);
             this.form = action.params.form;
             this.data = action.params.data;
             this.wizard_id = action.context.wizard | null;
             console.log('action', action)
             console.log('this.wizard_i', this.wizard_id)

//       start: function() {
//			var self = this;
//			self.initial_render = true;

//			rpc.query({
//				model: 'comprehensive.list.report',
//				method: 'create',
//				args: [{
//
//				}]
//			}).then(function(res) {
//				self.wizard_id = res;
//				self.load_data(self.initial_render);
//                self.apply_filter();
//			})
//		},

//       load_data: function(initial_render = true) {
//
//			var self = this;
//
//			self._rpc({
//				model: 'comprehensive.list.report',
//				method: 'comprehensive_list_report',
//				args: [
//					[this.wizard_id]
//				],
//
//			}).then(function(datas) {
//
//				if (initial_render) {
//					self.$('.filter_view_cl').html(QWeb.render('comprehensiveFilterView', {
//						filter_data: datas['filters'],
//
//					}));
//					self.$el.find('.report_type').select2({
//						placeholder: ' Report Type...',
//					});
//
//				}
//				if (datas['orders'])
//					self.$('.table_view_cl').html(QWeb.render('ComprehensiveTable', {
//						filter: datas['filters'],
//						order: datas['orders'],
//						budgetary_ids: datas['budgetary_ids'],
//						main_lines: datas['report_main_line']
//
//					}));
//			})
//		},

//		print_pdf: function(e) {
//			e.preventDefault();
//			var self = this;
//			var action_title = self._title;
//			console.log(self)
//			self._rpc({
//				model: 'comprehensive.list.report',
//				method: 'comprehensive_list_report',
//				args: [
//					[self.wizard_id]
//				],
//			}).then(function(data) {
//				var action = {
//					'type': 'ir.actions.report',
//					'report_type': 'qweb-pdf',
//					'report_name': 'account_budget_reports.comprehensive_list_report',
//					'report_file': 'account_budget_reports.comprehensive_list_report',
//					'data': {
//						'report_data': data
//					},
//					'context': {
//						'active_model': 'comprehensive.list.report',
//						'landscape': 1,
//						'comprehensive_list_view': true
//
//					},
//					'display_name': 'Comprehensive List Order',
//				};
//				return self.do_action(action);
//			});
//
//		},


   });
   core.action_registry.add("td4", TD4Reports);
   return TD4Reports;
});