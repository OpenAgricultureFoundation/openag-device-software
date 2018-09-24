var availableCultivars = {};  // By UUID
var availableCultivationMethods = {};  // By UUID

// ----- INIT -----
function initCultivars(){
    console.log("Initializing Cultivars")
    loadAvailableCultivars();
    loadAvailableCultivationMethods();
    initCultivarHandlers();
}


function initCultivarHandlers(){
    console.log("Initialiing Cultivar Handlers");

    params = [
        {"cults": availableCultivars, "selector": "#cultivars"},
        {"cults": availableCultivationMethods, "selector": "#cultivationMethods"}
    ];
    for (var i in params){
        var p = params[i];
        // Search
        $(p.selector + " .searchInput").keyup(
                cultSearchInputHandler.bind(null, p.cults, p.selector)
        );
        // Search results table on row click handler
        $(p.selector + " .searchResults tbody").on("click", "tr",
                cultSearchResultHandler.bind(null, p.cults, p.selector)
        );
        $(p.selector + " .searchResults tbody").on("click", ".addCult",
                addCultHandler.bind(null, p.cults, p.selector)
        );
        $(p.selector + " .selectedTable tbody").on("click", ".removeCult", removeCultHandler);
    };
}


function trFromHead(data, headSelector){
    var tr = '<tr>';
    $(headSelector + " th").each( function( index ){
        var jthis = $(this);
        var key = jthis.text().toLowerCase();
        tr += '<td>' + data[key] + '</td>';
    });
    tr += '</tr>';
    return tr;
}


function cultSearchInputHandler(cults, selector, event){
    var jtar = $(event.target);
    var val = jtar.val().toLowerCase();

    // Clear the table and details
    $(selector + " .searchResults tbody").empty();
    $(selector + " .searchDetails input").val("");
    $(selector + " .searchDetails textarea").val("");

    // Add any results to the table
    var matchingCults = 
        Object.values(cults)
        .filter(function( cult ){ return cult["name"].toLowerCase().includes(val) });
    console.log(selector + " search: " + matchingCults.length + " results for  " + val);

    for (var i in matchingCults){
        var c = matchingCults[i];
        var tr = trFromHead(c, selector + " .searchResults thead");
        $(selector + " .searchResults tbody").append(tr);
        $(selector + " .searchResults tbody tr").last().data("uuid", c["uuid"]);
        $(selector + " .searchResults tbody tr td").last().html(
                '<i class="addCult fas fa-plus"></i>');
    }
}


function cultSearchResultHandler(cults, selector, event){
    var jtar = $(event.target);
    var jrow = jtar.closest("tr");
    var uuid = jrow.data("uuid");
    var cult = cults[uuid];
    console.log("Displaying details for cult " + uuid + ":" + cult["name"]);

    for (var key in cult){
        var val = cult[key];
        $(selector + " .searchDetails [name=" + key + "]").val(val);
    }
}


function addCultHandler(cults, selector, event){
    var jtar = $(event.target);
    var jrow = jtar.closest("tr");
    var uuid = jrow.data("uuid");

    var c = cults[uuid];
    console.log("Adding cult" + uuid + ":" + c["name"]);

    // TODO fix this ass above
    var tr = trFromHead(c, selector + " .selectedTable thead");
    $(selector + " .selectedTable tbody").append(tr);
    $(selector + " .selectedTable tbody tr").last().data("uuid", c["uuid"]);
    $(selector + " .selectedTable tbody tr td").last().html(
            '<i class="removeCult fas fa-minus"></i>');
};


function removeCultHandler(event){
    var jtar = $(event.target);
    var jrow = jtar.closest("tr");

    console.log("Removing cult");
    jrow.remove();
};


// ----- Serializers -----
function getCultJson(cults, cardSelector){
    var data = [];
    $(cardSelector + " .selectedTable tbody tr").each( function( index ){
        var jthis = $(this);
        var uuid = jthis.data("uuid");
        data.push(cults[uuid]);
    });
    return data;
}
getCultivarsJson = getCultJson.bind(null, availableCultivars, "#cultivars");
getCultivationMethodsJson= getCultJson.bind(null, availableCultivationMethods, "#cultivationMethods");


// ----- Other -----
function loadAvailableCultivars(){
    console.log("Loading available cultivars")

    var local_cultivars = [
        {
            "name": "Scarlet Kale*",
            "description": "Red veined, tightly curled purple leaves.",
            "uuid": "d6d76ff9-b12e-47bb-8e83-f872c7870856",
            "link": "https://www.seedsavers.org/scarlet-kale",
            "average_height_centimeters": 80,
            "average_width_centimeters": 60,
            "average_duration_days": 60,
            "duration_start_stage": "seedling"
        }
    ];

    var django_cultivars_selection = []
    for (var i in django_cultivars){
        formatted_cultivar = {
            "name": django_cultivars[i]["name"],
            "description": django_cultivars[i]["info"]["description"]["brief"],
            "uuid": django_cultivars[i]["uuid"],
            "link": django_cultivars[i]["info"]["link"],
            "average_height_centimeters": django_cultivars[i]["info"]["average_height_centimeters"],
            "average_width_centimeters": django_cultivars[i]["info"]["average_width_centimeters"],
            "average_duration_days": django_cultivars[i]["info"]["average_duration_days"],
            "duration_start_stage": django_cultivars[i]["info"]["duration_start_stage"]

        }
        django_cultivars_selection[i] = formatted_cultivar;
    }

    cultivars_selection = django_cultivars_selection;
    // cultivars_selection = local_cultivars;

    // console.log(cultivars_selection)
    for (var i in cultivars_selection){
        var cultivar = cultivars_selection[i];
        availableCultivars[cultivar["uuid"]] = cultivar;
    }
}


function loadAvailableCultivationMethods(){
    console.log("Loading available cultivation methods")
	var local_cultivation_methods = [
        {
            "name": "Shallow Water Culture",
            "description": "A hydroponic cultivation method where plant roots sit in a mix of water and nutrients.Root zone depth is usually ten inches or less.",
            "uuid": "30cbbded-07a7-4c49-a47b-e34fc99eefd0"
        }
	];

    var django_cultivation_methods_selection = []
    for (var i in django_cultivation_methods){
        formatted_cultivation_method = {
            "name": django_cultivation_methods[i]["name"],
            "description": django_cultivation_methods[i]["info"]["description"]["verbose"],
            "uuid": django_cultivation_methods[i]["uuid"]
        }
        django_cultivation_methods_selection[i] = formatted_cultivation_method;
    }

    cultivation_methods_selection = django_cultivation_methods_selection;
    // cultivation_methods_selection = local_cultivation_methods;

    for (var i in cultivation_methods_selection){
        var c = cultivation_methods_selection[i];
        availableCultivationMethods[c["uuid"]] = c;
    }
}