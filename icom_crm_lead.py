# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


#Permet de faire les traductions avec la fonction _()

class CrmLead(models.Model):

    # Surcharge par héritage du modèle crm.lead
    _inherit = 'crm.lead'

    # Cette action permet de créer un nouveau projet avec les données de l'opportunité
    @api.multi
    def action_Lead2Project(self):
        for opportunity in self:
        # Recuperation de l'objet
    
            # Recuperation de l'action permettant d'acceder à la liste des projets
            # Dans ce cas, l'utisateur devra cliquer sur 'Créer' pour créer le projet, ce qui n'est pas très intuitif
            #res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'project', 'open_view_project_all', context)
    
            # Recuperation de l'action permettant d'acceder à l'agenda
            # Pour cela, j'ai créé une nouvelle action permettant de créer directement un projet
            # Comme cela, l'utilisateur n'a pas à cliquer sur 'Créer'
            res = self.env['ir.actions.act_window'].for_xml_id('icom_project', 'icom_action_create_project')
    
            # Initialisation du context avec les données de l'opportunité
            res['context'] = {
                'default_name': opportunity.name,
                'default_partner_id': opportunity.partner_id and opportunity.partner_id.id or False,
                'default_use_issues': False,
                'default_user_id': opportunity.user_id  and opportunity.user_id.id or False,
            }
            return res




