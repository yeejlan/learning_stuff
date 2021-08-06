let parseQueryString = function( queryString ) {
    let params = {}, queries, temp, i, l;

    queries = queryString.split("&");

    for ( i = 0, l = queries.length; i < l; i++ ) {
        temp = queries[i].split('=');
        params[temp[0]] = decodeURIComponent(temp[1]);
    }

    return params;
};

let _page_x_init = function(page) {
  page = page.replace('/','_');
  let page_idx = "_page_" + page;
  let page_context = window[page_idx];
  if(typeof page_context != 'function') {
    return;
  }
  let page_data = page_context();
  let data_stack = document.querySelector('#'+page_idx)._x_dataStack[0];
  for (let key in page_data){
    let value = data_stack[key] || page_data[key];
    data_stack[key] = value;
  }
}

let app = function() {
    return {
        page: 'index',
        uri: '#',
        params: {},
        content: "loading...",
        loadPage() {
          this.load_page(this.page, this.params);
        },
        load_page(page, data) {
          fetch(`/page/${page}.html`)
            .then((response) => response.text())
            .then((template) => {
              page = page.replace('/','_');
              let dataStr = JSON.stringify(data)
              let content = `<div id="_page_${page}" x-data=${dataStr} x-init="_page_x_init('${page}')">${template}</div>`;
              this.content = content;
            });
        },
        updatePageAndParams() {
            let hash = new URL(document.URL).hash;
            hash = hash.substring(1);
            let page = '';
            let params = {};
            let pos = hash.indexOf('?');
            if(pos == -1) {
              page = hash;
            }else{
              page = hash.substring(0, pos);
              let query_str = hash.substring(pos+ 1);
              params = parseQueryString(query_str);
            }
            page = page || 'index';
            this.params = params;
            this.page = page;
            this.uri = hash;
        },
        init(){
          this.updatePageAndParams();
          this.loadPage();
        }
    };
}
