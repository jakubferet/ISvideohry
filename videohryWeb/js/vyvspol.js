function getInputValue(id) {
  var inputValue = document.getElementById(id).value;
  return inputValue;
}

function ClearTable() {
  var inputValue = document.getElementById("zanr_id");
  var resultTable = document.getElementById("wrapper2");
  inputValue.value = "";
  resultTable.innerHTML = "";
}

function ShowTable(id, resolver) {
  var column;
  var query;
  var zanr_id = getInputValue("zanr_id");
  var wrapper = document.getElementById(id);
  wrapper.innerHTML = "";

  switch(resolver){
    case "vyvspolAll":
      column = ['id', 'nazev', 'zeme', 'pocet'];
      query = `query{vyvspolAll{id,nazev,zeme,pocet}}`;
      break;
    case "zamereni":
      column = ['ID', 'název', 'země', 'počet', 'žánr'];
      query = `query{zanr(id:${zanr_id}){zamereni{vyvspol{id,nazev,zeme,pocet},zanr{nazev}}}}`;
      break;
  }

  const grid = new gridjs.Grid({
    pagination: {
      limit: 10
    },
    search: true,
    sort: true,
  
    columns: column,
  
    server: {
      url: "http://localhost:31102/gql/",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query
      }),
      then: data => {
        switch(resolver){
          case "vyvspolAll":
            return data.data.vyvspolAll;
          case "zamereni":
            return data.data.zanr.zamereni.map(object => [object.vyvspol.id, object.vyvspol.nazev, object.vyvspol.zeme, object.vyvspol.pocet, object.zanr.nazev]);
        }
      },
    },
  }).render(wrapper);
  
  if (resolver == "zamereni"){
    grid.forceRender();
  }
}

function HttpRequest(resolver){
  var query;
  var vyvspol_nazev = getInputValue("vyvspol_nazev");
  var vyvspol_zeme = getInputValue("vyvspol_zeme");
  var vyvspol_pocet = getInputValue("vyvspol_pocet");
  var vyvspol_odstran = getInputValue("vyvspol_odstran");

  switch(resolver){
    case "createVyvspol":
      query = `mutation{createVyvspol(vyvspol:{nazev:"${vyvspol_nazev}",zeme:"${vyvspol_zeme}",pocet:${vyvspol_pocet}}){ok}}`;
      break;
    case "updateVyvspol":
      query = `mutation{updateVyvspol(vyvspol:{id:19,nazev:"vyvspol"}){ok}}`;
      break;
    case "deleteVyvspol":
      query = `mutation{deleteVyvspol(vyvspol:{id:${vyvspol_odstran}}){ok}}`;
      break;
  }
  fetch("http://localhost:31102/gql/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query
    }), 
  }).then(response => {
    return response.json();
  }).then(data => {
    console.log(data);
  });
}

ShowTable("wrapper1a", "vyvspolAll")