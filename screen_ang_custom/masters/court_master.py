# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json
import urllib

from odoo import fields, models, api, _
from odoo.tools import ustr
from odoo.exceptions import UserError, ValidationError


def geo_find(addr):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address='
    url += urllib.quote(addr.encode('utf8'))

    try:
        result = json.load(urllib.urlopen(url))
    except Exception as e:
        raise UserError(_('Network error'),
                             _('Cannot contact geolocation servers. Please make sure that your internet connection is up and running (%s).') % e)
    if result['status'] != 'OK':
        return None

    try:
        geo = result['results'][0]['geometry']['location']
        return float(geo['lat']), float(geo['lng']), url
    except (KeyError, ValueError):
        return None


def geo_query_address(street=None, tzip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        # put country qualifier in front, otherwise GMap gives wrong results,
        # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
        country = '{1} {0}'.format(*country.split(',',1))
    return ustr(', '.join(filter(None, [street,("%s %s" % (tzip or '', city or '')).strip(), state,country])))


class CourtMaster(models.Model):
    _name = 'court.master'

    @api.multi
    def _check_name(self):
        # if context is None:
        #     context = {}
        name = self.name
        searids = self.search([('name','=',name),('id','!=',self.id)])
        if len(searids)>0:
                return False
        return True
        
    @api.onchange('name','number')
    def onchange_number(self):
        if not self.name:
            return {'value': {'ref': False}}
        val = {
            'ref': (self.name and len(self.name)>=3 and self.name[:3].upper()+(self.number or '') or False)
        }
        return {'value': val}

    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            country_id = self.env['res.country.state'].browse(self.state_id.id).country_id.id
            return {'value':{'country_id':country_id}}
        return {}

    @api.onchange('district_id')
    def onchange_district(self):
        if self.district_id:
            state_id = self.env['district.district'].browse(self.district_id.id).state_id.id
            country_id = self.env['res.country.state'].browse(state_id.id).country_id.id
            return {'value':{'country_id':country_id,'state_id':state_id}}
        return {}

    name= fields.Char('Court Name',size=128, required=True)
    location= fields.Char('Court Location',size=128)
    number=fields.Char('Court No',size=64)
    ref=fields.Char('Court Id',size=20)
    street= fields.Char('Street', size=128)
    street2= fields.Char('Street2')
    zip= fields.Char('Zip', change_default=True, size=24)
    city= fields.Char('City', size=128)
    landmark=fields.Char('LandMark',size=128)
    district_id=fields.Many2one("district.district",'District')
    state_id= fields.Many2one("res.country.state", 'State')
    country_id= fields.Many2one('res.country', 'Country')
    active= fields.Boolean('Active')

    @api.multi
    def name_get(self):
        res = []
        # if not ids:
        #     return res
        for line in self:
            res.append((line.id,line.name+(line.city and ', '+line.city or '')+(line.district_id and ', '+line.district_id.name or '')+(line.state_id and ', '+line.state_id.name or '')))
        return res
        
    
    def geo_localize(self):
        # Don't pass context to browse()! We need country names in english below
        for partner in self:
            if not partner:
                continue
            url="http://maps.google.com/maps?oi=map&q="
        if partner.street:
            url+=partner.street.replace(' ','+')
        if partner.city:
            url+='+'+partner.city.replace(' ','+')
            if partner.state_id:
                url+='+'+partner.state_id.name.replace(' ','+')
        if partner.country_id:
            url+='+'+partner.country_id.name.replace(' ','+')
        if partner.zip:
            url+='+'+partner.zip.replace(' ','+')
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'target': 'new'
        }
        return True
    
    
        
    _constraints = [
        (_check_name, 'Court Name must be Unique!', []),
    ]
    
CourtMaster()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: