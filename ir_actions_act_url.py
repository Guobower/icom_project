# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.http import request



#TODO : Cette méthode par accèder à l'action en cours ne fonctionne pas,
# car elle necessite le rafraichissement du navigateur pour changer l'url du menu

#class IrActionsActUrl(models.Model):
#    _inherit = 'ir.actions.act_url'


#    @api.multi
#    def read(self, fields=None, load='_classic_read'):
#        result = super(IrActionsActUrl, self).read(fields, load=load)
#        if load=='_classic_read':
#            if result[0]['name']==u'is_tache_en_cours_url':
#                user = self.env['res.users'].browse(self._uid)
#                task_id=self.env['project.task']._compteur_en_cours()
#                res={}
#                if task_id:
#                    res={
#                        'name': 'Tache en cours',
#                        'view_mode': 'form',
#                        'view_type': 'form',
#                        'res_model': 'project.task',
#                        'res_id': task_id,
#                        'type': 'ir.actions.act_window',
#                    }
#                return [res]
#        return result



