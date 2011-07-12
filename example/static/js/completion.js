Site = window.Site || {};

(function(S, $) {

  var Autocompletion = function(options) {
    this.options = options || {};
    this.default_url = '/autocomplete/';
    
    this.result_class = this.options.result_class || 'ui-autocomplete-result';
    this.remove_selector = this.options.remove_selector || '.' + this.result_class;
  };

  Autocompletion.prototype.bind_listener = function(input_sel, hidden_sel) {
    var self = this;

    this.input_element = $(input_sel);
    this.hidden_element = $(hidden_sel);

    this.input_element.autocomplete({
      minLength: self.options.min_length || 2,
      select: function(e, ui) {self.select_result(ui.item);},
      source: function(request, response) {self.fetch_results(request, response);},
    });
    
    $(this.remove_selector).live('click', function(e) {
      e.preventDefault();
      var django_id = this.hash.slice(1);
      var hidden_id_list = self.hidden_element.val().split(',');
      new_ids = remove_from_list(hidden_id_list, django_id);
      self.hidden_element.val(new_ids.join(','));
      $(this).remove();
    });
  };
  
  Autocompletion.prototype.select_result = function(item) {
    var elem = $('<a href="#'+item.id+'" title="click to remove" class="'+this.result_class+'">'+item.label+' <strong>x</strong></a>');
    elem.insertAfter(this.input_element);
    
    var current = this.hidden_element.val();
    this.hidden_element.val(current+item.id+',');
  };
  
  Autocompletion.prototype.fetch_results = function(request, response) {
    var url = this.options.url || this.default_url,
        term = request.term;

    $.getJSON(url, {'q': term}, function(data) {
      var results = [];
      $.each(data, function(k, v) {
        v.label = v.title;
        v.value = '';
        v.id = v.django_ct + ':' + v.object_id;
        results.push(v);
      });
      response(results);
    });
  };
  
  function remove_from_list(list, val) {
    var new_list = [];
    for (var i = 0; i < list.length; i++) {
      if (list[i] != val) {
        new_list.push(list[i]);
      }
    }
    return new_list;
  };

  S.Autocompletion = Autocompletion;

})(Site, jQuery);
