openerp.web.legale = function (instance) {
var _t = instance.web._t,
    _lt = instance.web._lt;
var QWeb = instance.web.qweb;
instance.web.views.add('list', 'instance.web.LListView');
instance.web.LListView = instance.web.ListView.extend( /** @lends instance.web.ListView# */ {
  

    /**
     * Retrieves the view's number of records per page (|| section)
     *
     * options > defaults > parent.action.limit > indefinite
     *
     * @returns {Number|null}
     */
    limit: function () {
        if (this._limit === undefined) {
            this._limit = (this.options.limit
                        || this.defaults.limit
                        || (this.getParent().action || {}).limit
                        || 200);
        }
        return this._limit;
    },
});
};
// vim:et fdc=0 fdl=0 foldnestmax=3 fdm=syntax:
