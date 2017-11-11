# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import datetime
from dateutil import parser
from openerp.exceptions import Warning


class TaskCompteurDescription(models.TransientModel):
    _name  = 'is.project.task.compteur.description'

    commentaire = fields.Char('Description', required=False)

    @api.multi
    def demarrer_compteur(self):
        for obj in self:
            active_id=self._context['active_id']
            task=self.env['project.task'].browse(active_id)
            if task:
                vals={
                    'task_id'       : task.id,
                    'heure_debut'   : fields.datetime.now(),
                    'utilisateur_id': self._uid,
                    'commentaire'   : obj.commentaire,
                }
                new_id=self.env['is.project.task.compteur'].create(vals)


    @api.multi
    def compteur_en_cours(self):
        for obj in self:
            active_id=self._context['active_id']
            task=self.env['project.task'].browse(active_id)
            if task:
                task_id=task._compteur_en_cours()
                return {
                    'name': u'Tâches',
                    'view_mode': 'form,tree',
                    'view_type': 'form',
                    'res_id'   : task_id,
                    'res_model': 'project.task',
                    'type'     : 'ir.actions.act_window',
                }





class TaskCompteur(models.Model):
    _name  = 'is.project.task.compteur'
    _order = 'heure_debut'

    task_id        = fields.Many2one('project.task', 'Tâcĥe', required=True, ondelete='cascade', readonly=True, select=True)
    heure_debut    = fields.Datetime(string='Heure de début')
    utilisateur_id = fields.Many2one('res.users', 'Utilisateur', select=True)
    commentaire    = fields.Char(string='Description')


class Task(models.Model):
    _inherit = 'project.task'

    @api.multi
    @api.depends('date_end')
    def _week_date_end(self):
        result = {}
        for rec in self:
            semaine=""
            # Recupère la date au format string
            s = rec.date_end # 2013-09-25 22:41:04
            if s:
              # Convertir la date en objet datetime
              dt = parser.parse(s)
              # Cette fonction retourne un tableau avec l'annee, la semaine et le jour dans la semaine
              if dt:
                t=dt.isocalendar()
                # Recuperation de la semaine dans le tableau
                semaine=str(t[0])+"-S"+str(t[1])
            rec.week_date_end = semaine


    week_date_end = fields.Char(compute='_week_date_end', string='Semaine', store=True, readonly=True)
    compteur_ids  = fields.One2many('is.project.task.compteur'  , 'task_id', u"Compteurs")


    @api.multi
    def _compteur_en_cours(self):
        cr=self._cr
        sql="""
            select task_id
            from is_project_task_compteur
            where utilisateur_id="""+str(self._uid)+"""
        """
        cr.execute(sql)
        task_id=False
        for row in cr.fetchall():
            task_id=row[0]
        return task_id





    @api.multi
    def demarrer_compteur(self):
        for obj in self:
            task_id=self._compteur_en_cours()
            if task_id:
                view_id=self.env['ir.model.data'].get_object_reference('icom_project', 'is_project_task_compteur_message_form_view')
                return {
                    'name': u'Démarrer le compteur',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id'  : view_id[1],
                    'res_model': 'is.project.task.compteur.description',
                    'target'   : 'new',
                    'type'     : 'ir.actions.act_window',
                }
            return {
                'name': u'Démarrer le compteur',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'is.project.task.compteur.description',
                'target'   : 'new',
                'type'     : 'ir.actions.act_window',
            }



    @api.multi
    def arreter_compteur(self):
        for obj in self:
            for line in obj.compteur_ids:
                if self._uid==line.utilisateur_id.id:
                    debut = int(datetime.datetime.strptime(line.heure_debut, '%Y-%m-%d %H:%M:%S').strftime('%s'))
                    fin   = int(fields.datetime.now().strftime('%s'))
                    duree=(fin-debut)
                    duree=duree/3600.0
                    vals={
                        'project_id' : obj.project_id.id,
                        'task_id'    : obj.id,
                        'date'       : fields.datetime.now(),
                        'user_id'    : self._uid,
                        'unit_amount': duree,
                        'name'       : line.commentaire,
                    }
                    new_id=self.env['account.analytic.line'].create(vals)
                    line.unlink()


