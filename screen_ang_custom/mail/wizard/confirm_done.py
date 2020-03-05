# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ConfirmDone(models.TransientModel):
    _name = "confirm.done"
    _description = "Mark Selected Tasks as Done"

    name=fields.Char('Do you want to Make selected Tasks as Done?', size=64)

    
    @api.multi
    def button_confirm(self):
        if 'active_ids' in self._context:
            vals = {}
            vals['remaining_hours'] = 0.0
            vals['state']='done'
            stage_id = False
            comids = self.env['project.task.type'].search([('name','=','Completed'),('state','=','done')])
            if comids and len(comids):
                vals['stage_id']=comids[0]
                stage_id = comids[0]
            
            actids = tuple(self._context['active_ids'])
            if len(self._context['active_ids'])>1:
                qry = "update project_task set remaining_hours=0.0, state='done', flg_message=True,progress=100, stage_id="+str(stage_id.id)+" where id in "+str(actids)+""
            else:
                qry = "update project_task set remaining_hours=0.0, state='done', flg_message=True,progress=100, stage_id="+str(stage_id.id)+" where id ="+str(self._context['active_ids'][0])+""
            self.env.cr.execute(qry)
        return True
        
ConfirmDone()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
