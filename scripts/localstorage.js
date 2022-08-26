cookieSettingsName = "hbjson_settings";
settingsValidity = 5;	    // 5 days
settings = [{ name: "openbridges", "open": true }, { "map": { "zoom" : 6.5 } }, {"name": "masters", "open": true }, { "name": "peers", "open": true }];

// localStorage.setItem('theme', themeName);
// localStorage.getItem('theme', themeName);

var names = [];    

names["Andre"] = "André";
names["Francois"] = "François";
names["Herve"] = "Hervé";
names["Jerome"] = "Jérôme";
names["Jerôme"] = "Jérôme";
names["Stephane"] = "Stéphane";
names["Gerard"] = "Gérard";
names["Jean-Noel"] = "Jean-Noël";
names["Remi"] = "Rémi";
names["Clement"] = "Clément";
names["Frederic"] = "Frédéric";
names["Jeremy"] = "Jérémy";
names["Jean-Francois"] = "Jean-François";
names["Gregory"] = "Grégory";    
names["Anne-Cecile"] = "Anne-Cécile";
names["Mickael"] = "Mickaël";
names["Theophile"] = "Théophile";
names["Sebastien"] = "Sébastien";
names["Sbastien"] = "Sébastien";
names["Raphael"] = "Raphaël";
names["Cedric"] = "Cédric";
names["Rene"] = "René";
names["Nathanael"] = "Nathanaël";
names["Joel"] = "Joël";
names["Jeremie"] = "Jérémie";

String.prototype.capitalize = function (lower) {
    return (lower ? this.toLowerCase() : this).replace(/(?:^|\s|['`‘’.-])[^\x00-\x60^\x7B-\xDF](?!(\s|$))/g, function (a) {
        return a.toUpperCase();
    });
};

function enhanceNames(name) {
    if (name != null) {
        name = name.replace(/None/g, "");

        if (names != null && names[name] != null)
            return names[name].capitalize(true);
    }

    return name.capitalize(true);
}

function createCookie(name, value, days) {
    var expires;

    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    } else {
        expires = "";
    }
    
    document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + expires + "; path=/";
}

function readCookie(name) {
    var nameEQ = encodeURIComponent(name) + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
            return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

function getTgTableState(name) {
    for(let i=0; i < settings.length; i++) {
        if (settings[i].name != null && settings[i].name == name)
            return settings[i];
    }

    return null;
}

function saveSettings() {
    themeSettings = document.documentElement.className;
    settings = [
        { "config": { "theme": themeSettings, hidetg: hideAllTG } },
        { "map": { "zoom" : (map != null) ? map.getZoom() : 6.5 } },
        { "name": "openbridges",    "open": $('#openbridges').is(':visible'), "colspan": $("#theadOpenbridges tr th").length }, 
        { "name": "masters",        "open": $('#masters').is(':visible'), "colspan": $("#theadMasters tr th").length }, 
        { "name": "peers",          "open": $('#peers').is(':visible'), "colspan": $("#theadPeers tr th").length }
    ];

    if (tgorder != null) {
        tgorder.forEach(tg => {
            var tgName = "tgId"+tg;
            var tgId = "hblink"+tg;
            if (document.getElementById(tgName) != null)
                settings.push({ "name": tgId, "open": $("#" + tgId).is(":visible"), "colspan": $("#" + tgName + " tr th").length });
        });
    }
    
    createCookie(cookieSettingsName, JSON.stringify(settings), settingsValidity);

    alert("Sauvegarde effectuée");
}

function eraseCookie(name) {
    createCookie(name, "", -1);
}    

function adjustTheme() {
    if (themeSettings == "auto") {
        var hr = new Date().getHours();
        // choose dark netween 10PM and 7AM
        if (hr > 22 && hr < 7) {
            if (document.documentElement.className != "theme-dark")
                document.documentElement.className = "theme-dark";
        }
        else {
            if (document.documentElement.className != "theme-light")
                document.documentElement.className = "theme-light";
        }
    }
}

function getConfigFromLocalStorage() {
    map = null;

    // retrieve settings
    if ((cookie = JSON.parse(readCookie(cookieSettingsName))) == null) {
        cookie = settings;
        createCookie(cookieSettingsName, JSON.stringify(settings), settingsValidity);
    }
    else    
        settings = cookie;

    themeSettings = "theme-dark";

    for(let i=0; i < settings.length; i++) {
        var tbs = settings[i];

        if (tbs.config) {
            themeSettings = tbs.config.theme;
            hideAllTG = tbs.config.hidetg;

            if (themeSettings == "auto")
                adjustTheme();
            else
                document.documentElement.className = themeSettings;
        }
        else {            
            if (tbs.map) {
                currentZoom = tbs.map.zoom;
            }
            else {
                if (tbs.open) {
                    $("#"+tbs.name).show();
                    // var count = tbs.colspan;
                    // if (count == null)
                    //     count = 5;
                    // $("#"+tbs.name).append("<tr><td class='infoline' colspan="+(count+1)+">Mise à jour au prochain appel entrant...</td></tr>");
                }
                else
                    $("#"+tbs.name).hide();
            }
        }
    }
}

function getTgFlag(id) {
    if (id.length > 2 && parseInt(id) > 100) {
        id = id.substring(0, 3);

        switch (id) {
            case "736":
            case "994":
                return "unlicenced.png"

            case "206":
                return "be.png";
            case "214":
                return "es.png";
            case "228":
                return "ch.png";
            case "262":
            case "264":
                return "de.png";

            case "102":
            case "302":
                return "ca.png";

            case "604":
                return "ma.png";

            case "340":
            case "546":
            case "547":
            case "742":
            case "647":
            case "208":
                return "fr.png";

            default:
                break;
        }

        for (let i = 0; i < mcc.length; i++) {
            if (mcc[i].dmrid == id)
                return "https://flagcdn.com/h20/" + mcc[i].code.toLowerCase() + ".png";
        }
    }

    return "shield.png";
}

function getFlag(callsign, dmrid) {
    if (dmrid.length > 2 && parseInt(dmrid) > 100) {
        // check if beacon has specific bitmap
        for (var key in tgbeacons) {
            if (dmrid == key)
                return tgbeacons[key];
        }

        dmrid = dmrid.substring(0, 3);

        if (callsign.startsWith("FS"))
            return "shield.png";

        if (callsign.startsWith("14FRS") || callsign.startsWith("FRS"))
            return "frs.png";

        if (callsign.startsWith("BALISE") || dmrid.startsWith(14))
            return "unlicenced.png";

        switch (dmrid) {
            case "736":
                if (dmrid.indexOf(callsign) != -1) break; // else fall through
            case "994":
                return "unlicenced.png"

            case "206":
                return "be.png";
            case "214":
                return "es.png";
            case "228":
                return "ch.png";
            case "262":
            case "264":
                return "de.png";

            case "102":
            case "302":
                return "ca.png";

            case "604":
                return "ma.png";

            case "340":
            case "546":
            case "547":
            case "742":
            case "647":
            case "208":
                return "fr.png";

            default:
                break;
        }

        for (let i = 0; i < mcc.length; i++) {
            if (mcc[i].dmrid == dmrid)
                return "https://flagcdn.com/h20/" + mcc[i].code.toLowerCase() + ".png";
        }
    }

    return "noflag.png";
}

mcc = [
{
	"dmrid": "653",
	"country": "Eswatini",
	"code": "SZ"
},
{
	"dmrid": "225",
    "country": "Vatican City",
    "code": "VA"
},
{
	"dmrid": "425",
    "country": "Palestinian Authority",
    "code": "PS"
},
{
	"dmrid": "255",
    "country": "Ukraine",
    "code": "UA"
},
{
    "dmrid": "111",
    "country": "United States of America",
    "code": "US"
},
{
    "dmrid": "113",
    "country": "United States of America",
    "code": "US"
},
{
    "dmrid": "202",
    "country": "Greece",
    "code": "GR"
},
{
    "dmrid": "204",
    "country": "Netherlands",
    "code": "NL"
},
{
    "dmrid": "206",
    "country": "Belgium",
    "code": "BE"
},
{
    "dmrid": "208",
    "country": "France",
    "code": "FR"
},
{
    "dmrid": "212",
    "country": "Monaco",
    "code": "MC"
},
{
    "dmrid": "213",
    "country": "Andorra",
    "code": "AD"
},
{
    "dmrid": "214",
    "country": "Spain",
    "code": "ES"
},
{
    "dmrid": "216",
    "country": "Hungary",
    "code": "HU"
},
{
    "dmrid": "218",
    "country": "Bosnia and Herzegovina",
    "code": "BA"
},
{
    "dmrid": "219",
    "country": "Croatia",
    "code": "HR"
},
{
    "dmrid": "220",
    "country": "Serbia",
    "code": "RS"
},
{
    "dmrid": "221",
    "country": "Kosovo",
    "code": "XK"
},
{
    "dmrid": "222",
    "country": "Italy",
    "code": "IT"
},
{
    "dmrid": "226",
    "country": "Romania",
    "code": "RO"
},
{
    "dmrid": "228",
    "country": "Switzerland",
    "code": "CH"
},
{
    "dmrid": "230",
    "country": "Czech Republic",
    "code": "CZ"
},
{
    "dmrid": "231",
    "country": "Slovakia",
    "code": "SK"
},
{
    "dmrid": "232",
    "country": "Austria",
    "code": "AT"
},
{
    "dmrid": "234",
    "country": "United Kingdom",
    "code": "GB"
},
{
    "dmrid": "235",
    "country": "United Kingdom",
    "code": "GB"
},
{
    "dmrid": "300",
    "country": "United Kingdom",
    "code": "GB"
},
{
    "dmrid": "238",
    "country": "Denmark",
    "code": "DK"
},
{
    "dmrid": "240",
    "country": "Sweden",
    "code": "SE"
},
{
    "dmrid": "242",
    "country": "Norway",
    "code": "NO"
},
{
    "dmrid": "244",
    "country": "Finland",
    "code": "FI"
},
{
    "dmrid": "246",
    "country": "Lithuania",
    "code": "LT"
},
{
    "dmrid": "247",
    "country": "Latvia",
    "code": "LV"
},
{
    "dmrid": "248",
    "country": "Estonia",
    "code": "EE"
},
{
    "dmrid": "250",
    "country": "Russian Federation",
    "code": "RU"
},
{
    "dmrid": "257",
    "country": "Belarus",
    "code": "BY"
},
{
    "dmrid": "259",
    "country": "Moldova",
    "code": "MD"
},
{
    "dmrid": "260",
    "country": "Poland",
    "code": "PL"
},
{
    "dmrid": "262",
    "country": "Germany",
    "code": "DE"
},
{
    "dmrid": "263",
    "country": "Germany",
    "code": "DE"
},
{
    "dmrid": "266",
    "country": "Gibraltar",
    "code": "GI"
},
{
    "dmrid": "268",
    "country": "Portugal",
    "code": "PT"
},
{
    "dmrid": "270",
    "country": "Luxembourg",
    "code": "LU"
},
{
    "dmrid": "272",
    "country": "Republic of Ireland",
    "code": "IE"
},
{
    "dmrid": "274",
    "country": "Iceland",
    "code": "IS"
},
{
    "dmrid": "276",
    "country": "Albania",
    "code": "AL"
},
{
    "dmrid": "278",
    "country": "Malta",
    "code": "MT"
},
{
    "dmrid": "280",
    "country": "Cyprus",
    "code": "CY"
},
{
    "dmrid": "282",
    "country": "Georgia",
    "code": "GE"
},
{
    "dmrid": "283",
    "country": "Armenia",
    "code": "AM"
},
{
    "dmrid": "284",
    "country": "Bulgaria",
    "code": "BG"
},
{
    "dmrid": "286",
    "country": "Turkey",
    "code": "TR"
},
{
    "dmrid": "288",
    "country": "Faroe Islands",
    "code": "FO"
},
{
    "dmrid": "289",
    "country": "Abkhazia",
    "code": "AB"
},
{
    "dmrid": "290",
    "country": "Greenland",
    "code": "GL"
},
{
    "dmrid": "292",
    "country": "San Marino",
    "code": "SM"
},
{
    "dmrid": "293",
    "country": "Slovenia",
    "code": "SI"
},
{
    "dmrid": "294",
    "country": "Republic of North Macedonia",
    "code": "MK"
},
{
    "dmrid": "295",
    "country": "Liechtenstein",
    "code": "LI"
},
{
    "dmrid": "297",
    "country": "Montenegro",
    "code": "ME"
},
{
    "dmrid": "302",
    "country": "Canada",
    "code": "CA"
},
{
    "dmrid": "308",
    "country": "Saint Pierre and Miquelon",
    "code": "PM"
},
{
    "dmrid": "310",
    "country": "United States of America",
    "code": "US"
},
{
    "dmrid": "311",
    "country": "United States of America",
    "code": "US"
},
{
    "dmrid": "312",
    "country": "United States of America",
    "code": "US"
},
{
    "dmrid": "313",
    "country": "United States of America",
    "code": "US"
},
{
    "dmrid": "314",
    "country": "United States of America",
    "code": "US"
},
{
    "dmrid": "315",
    "country": "United States of America",
    "code": "US"
},
{
    "dmrid": "316",
    "country": "United States of America",
    "code": "US"
},
{
    "dmrid": "317",
    "country": "United States of America",
    "code": "US"
},
{
    "dmrid": "318",
    "country": "United States of America",
    "code": "US"
},
{
    "dmrid": "330",
    "country": "Puerto Rico",
    "code": "PR"
},
{
    "dmrid": "334",
    "country": "Mexico",
    "code": "MX"
},
{
    "dmrid": "338",
    "country": "Jamaica",
    "code": "JM"
},
{
    "dmrid": "340",
    "country": "French Antilles",
    "code": "BL"
},
{
    "dmrid": "342",
    "country": "Barbados",
    "code": "BB"
},
{
    "dmrid": "344",
    "country": "Antigua and Barbuda",
    "code": "AG"
},
{
    "dmrid": "346",
    "country": "Cayman Islands",
    "code": "KY"
},
{
    "dmrid": "348",
    "country": "British Virgin Islands",
    "code": "VG"
},
{
    "dmrid": "350",
    "country": "Bermuda",
    "code": "BM"
},
{
    "dmrid": "352",
    "country": "Grenada",
    "code": "GD"
},
{
    "dmrid": "354",
    "country": "Montserrat",
    "code": "MS"
},
{
    "dmrid": "356",
    "country": "Saint Kitts and Nevis",
    "code": "KN"
},
{
    "dmrid": "358",
    "country": "Saint Lucia",
    "code": "LC"
},
{
    "dmrid": "360",
    "country": "Saint Vincent and the Grenadines",
    "code": "VC"
},
{
    "dmrid": "362",
    "country": "Former Netherlands Antilles",
    "code": "BQ"
},
{
    "dmrid": "363",
    "country": "Aruba",
    "code": "AW"
},
{
    "dmrid": "364",
    "country": "Bahamas",
    "code": "BS"
},
{
    "dmrid": "365",
    "country": "Anguilla",
    "code": "AI"
},
{
    "dmrid": "366",
    "country": "Dominica",
    "code": "DM"
},
{
    "dmrid": "368",
    "country": "Cuba",
    "code": "CU"
},
{
    "dmrid": "370",
    "country": "Dominican Republic",
    "code": "DO"
},
{
    "dmrid": "372",
    "country": "Haiti",
    "code": "HT"
},
{
    "dmrid": "374",
    "country": "Trinidad and Tobago",
    "code": "TT"
},
{
    "dmrid": "376",
    "country": "Turks and Caicos Islands",
    "code": "TC"
},
{
    "dmrid": "400",
    "country": "Azerbaijan",
    "code": "AZ"
},
{
    "dmrid": "401",
    "country": "Kazakhstan",
    "code": "KZ"
},
{
    "dmrid": "402",
    "country": "Bhutan",
    "code": "BT"
},
{
    "dmrid": "404",
    "country": "India",
    "code": "IN"
},
{
    "dmrid": "405",
    "country": "India",
    "code": "IN"
},
{
    "dmrid": "410",
    "country": "Pakistan",
    "code": "PK"
},
{
    "dmrid": "412",
    "country": "Afghanistan",
    "code": "AF"
},
{
    "dmrid": "413",
    "country": "Sri Lanka",
    "code": "LK"
},
{
    "dmrid": "414",
    "country": "Myanmar",
    "code": "MM"
},
{
    "dmrid": "415",
    "country": "Lebanon",
    "code": "LB"
},
{
    "dmrid": "416",
    "country": "Jordan",
    "code": "JO"
},
{
    "dmrid": "417",
    "country": "Syria",
    "code": "SY"
},
{
    "dmrid": "418",
    "country": "Iraq",
    "code": "IQ"
},
{
    "dmrid": "419",
    "country": "Kuwait",
    "code": "KW"
},
{
    "dmrid": "420",
    "country": "Saudi Arabia",
    "code": "SA"
},
{
    "dmrid": "421",
    "country": "Yemen",
    "code": "YE"
},
{
    "dmrid": "422",
    "country": "Oman",
    "code": "OM"
},
{
    "dmrid": "424",
    "country": "United Arab Emirates",
    "code": "AE"
},
{
    "dmrid": "425",
    "country": "Israel",
    "code": "IL"
},
{
    "dmrid": "426",
    "country": "Bahrain",
    "code": "BH"
},
{
    "dmrid": "427",
    "country": "Qatar",
    "code": "QA"
},
{
    "dmrid": "428",
    "country": "Mongolia",
    "code": "MN"
},
{
    "dmrid": "429",
    "country": "Nepal",
    "code": "NP"
},
{
    "dmrid": "432",
    "country": "Iran",
    "code": "IR"
},
{
    "dmrid": "434",
    "country": "Uzbekistan",
    "code": "UZ"
},
{
    "dmrid": "436",
    "country": "Tajikistan",
    "code": "TJ"
},
{
    "dmrid": "437",
    "country": "Kyrgyzstan",
    "code": "KG"
},
{
    "dmrid": "438",
    "country": "Turkmenistan",
    "code": "TM"
},
{
    "dmrid": "440",
    "country": "Japan",
    "code": "JP"
},
{
    "dmrid": "441",
    "country": "Japan",
    "code": "JP"
},
{
    "dmrid": "450",
    "country": "South Korea",
    "code": "KR"
},
{
    "dmrid": "452",
    "country": "Vietnam",
    "code": "VN"
},
{
    "dmrid": "454",
    "country": "Hong Kong",
    "code": "HK"
},
{
    "dmrid": "455",
    "country": "Macao",
    "code": "MO"
},
{
    "dmrid": "456",
    "country": "Cambodia",
    "code": "KH"
},
{
    "dmrid": "457",
    "country": "Laos",
    "code": "LA"
},
{
    "dmrid": "460",
    "country": "China",
    "code": "CN"
},
{
    "dmrid": "466",
    "country": "Taiwan",
    "code": "TW"
},
{
    "dmrid": "467",
    "country": "North Korea",
    "code": "KP"
},
{
    "dmrid": "470",
    "country": "Bangladesh",
    "code": "BD"
},
{
    "dmrid": "472",
    "country": "Maldives",
    "code": "MV"
},
{
    "dmrid": "502",
    "country": "Malaysia",
    "code": "MY"
},
{
    "dmrid": "505",
    "country": "Australia",
    "code": "AU"
},
{
    "dmrid": "510",
    "country": "Indonesia",
    "code": "ID"
},
{
    "dmrid": "514",
    "country": "East Timor",
    "code": "TL"
},
{
    "dmrid": "515",
    "country": "Philippines",
    "code": "PH"
},
{
    "dmrid": "520",
    "country": "Thailand",
    "code": "TH"
},
{
    "dmrid": "525",
    "country": "Singapore",
    "code": "SG"
},
{
    "dmrid": "528",
    "country": "Brunei",
    "code": "BN"
},
{
    "dmrid": "530",
    "country": "New Zealand",
    "code": "NZ"
},
{
    "dmrid": "536",
    "country": "Nauru",
    "code": "NR"
},
{
    "dmrid": "537",
    "country": "Papua New Guinea",
    "code": "PG"
},
{
    "dmrid": "539",
    "country": "Tonga",
    "code": "TO"
},
{
    "dmrid": "540",
    "country": "Solomon Islands",
    "code": "SB"
},
{
    "dmrid": "541",
    "country": "Vanuatu",
    "code": "VU"
},
{
    "dmrid": "542",
    "country": "Fiji",
    "code": "FJ"
},
{
    "dmrid": "543",
    "country": "Wallis and Futuna",
    "code": "WF"
},
{
    "dmrid": "544",
    "country": "American Samoa",
    "code": "AS"
},
{
    "dmrid": "545",
    "country": "Kiribati",
    "code": "KI"
},
{
    "dmrid": "546",
    "country": "New Caledonia",
    "code": "NC"
},
{
    "dmrid": "547",
    "country": "French Polynesia",
    "code": "PF"
},
{
    "dmrid": "548",
    "country": "Cook Islands",
    "code": "CK"
},
{
    "dmrid": "549",
    "country": "Samoa",
    "code": "WS"
},
{
    "dmrid": "550",
    "country": "Federated States of Micronesia",
    "code": "FM"
},
{
    "dmrid": "551",
    "country": "Marshall Islands",
    "code": "MH"
},
{
    "dmrid": "552",
    "country": "Palau",
    "code": "PW"
},
{
    "dmrid": "553",
    "country": "Tuvalu",
    "code": "TV"
},
{
    "dmrid": "554",
    "country": "Tokelau",
    "code": "TK"
},
{
    "dmrid": "555",
    "country": "Niue",
    "code": "NU"
},
{
    "dmrid": "602",
    "country": "Egypt",
    "code": "EG"
},
{
    "dmrid": "603",
    "country": "Algeria",
    "code": "DZ"
},
{
    "dmrid": "604",
    "country": "Morocco",
    "code": "MA"
},
{
    "dmrid": "605",
    "country": "Tunisia",
    "code": "TN"
},
{
    "dmrid": "606",
    "country": "Libya",
    "code": "LY"
},
{
    "dmrid": "607",
    "country": "Gambia",
    "code": "GM"
},
{
    "dmrid": "608",
    "country": "Senegal",
    "code": "SN"
},
{
    "dmrid": "609",
    "country": "Mauritania",
    "code": "MR"
},
{
    "dmrid": "610",
    "country": "Mali",
    "code": "ML"
},
{
    "dmrid": "611",
    "country": "Guinea",
    "code": "GN"
},
{
    "dmrid": "612",
    "country": "Ivory Coast",
    "code": "CI"
},
{
    "dmrid": "613",
    "country": "Burkina Faso",
    "code": "BF"
},
{
    "dmrid": "614",
    "country": "Niger",
    "code": "NE"
},
{
    "dmrid": "615",
    "country": "Togo",
    "code": "TG"
},
{
    "dmrid": "616",
    "country": "Benin",
    "code": "BJ"
},
{
    "dmrid": "617",
    "country": "Mauritius",
    "code": "MU"
},
{
    "dmrid": "618",
    "country": "Liberia",
    "code": "LR"
},
{
    "dmrid": "619",
    "country": "Sierra Leone",
    "code": "SL"
},
{
    "dmrid": "620",
    "country": "Ghana",
    "code": "GH"
},
{
    "dmrid": "621",
    "country": "Nigeria",
    "code": "NG"
},
{
    "dmrid": "622",
    "country": "Chad",
    "code": "TD"
},
{
    "dmrid": "623",
    "country": "Central African Republic",
    "code": "CF"
},
{
    "dmrid": "624",
    "country": "Cameroon",
    "code": "CM"
},
{
    "dmrid": "625",
    "country": "Cape Verde",
    "code": "CV"
},
{
    "dmrid": "626",
    "country": "São Tomé and Príncipe",
    "code": "ST"
},
{
    "dmrid": "627",
    "country": "Equatorial Guinea",
    "code": "GQ"
},
{
    "dmrid": "628",
    "country": "Gabon",
    "code": "GA"
},
{
    "dmrid": "629",
    "country": "Republic of the Congo",
    "code": "CG"
},
{
    "dmrid": "630",
    "country": "Democratic Republic of the Congo",
    "code": "CD"
},
{
    "dmrid": "631",
    "country": "Angola",
    "code": "AO"
},
{
    "dmrid": "632",
    "country": "Guinea-Bissau",
    "code": "GW"
},
{
    "dmrid": "633",
    "country": "Seychelles",
    "code": "SC"
},
{
    "dmrid": "634",
    "country": "Sudan",
    "code": "SD"
},
{
    "dmrid": "635",
    "country": "Rwanda",
    "code": "RW"
},
{
    "dmrid": "636",
    "country": "Ethiopia",
    "code": "ET"
},
{
    "dmrid": "637",
    "country": "Somalia",
    "code": "SO"
},
{
    "dmrid": "638",
    "country": "Djibouti",
    "code": "DJ"
},
{
    "dmrid": "639",
    "country": "Kenya",
    "code": "KE"
},
{
    "dmrid": "640",
    "country": "Tanzania",
    "code": "TZ"
},
{
    "dmrid": "641",
    "country": "Uganda",
    "code": "UG"
},
{
    "dmrid": "642",
    "country": "Burundi",
    "code": "BI"
},
{
    "dmrid": "643",
    "country": "Mozambique",
    "code": "MZ"
},
{
    "dmrid": "645",
    "country": "Zambia",
    "code": "ZM"
},
{
    "dmrid": "646",
    "country": "Madagascar",
    "code": "MG"
},
{
    "dmrid": "647",
    "country": "French Departments and Territories in the Indian Ocean",
    "code": "RE"
},
{
    "dmrid": "648",
    "country": "Zimbabwe",
    "code": "ZW"
},
{
    "dmrid": "649",
    "country": "Namibia",
    "code": "NA"
},
{
    "dmrid": "650",
    "country": "Malawi",
    "code": "MW"
},
{
    "dmrid": "651",
    "country": "Lesotho",
    "code": "LS"
},
{
    "dmrid": "652",
    "country": "Botswana",
    "code": "BW"
},
{
    "dmrid": "653",
    "country": "Swaziland",
    "code": "SZ"
},
{
    "dmrid": "654",
    "country": "Comoros",
    "code": "KM"
},
{
    "dmrid": "655",
    "country": "South Africa",
    "code": "ZA"
},
{
    "dmrid": "657",
    "country": "Eritrea",
    "code": "ER"
},
{
    "dmrid": "658",
    "country": "Saint Helena, Ascension and Tristan da Cunha",
    "code": "SH"
},
{
    "dmrid": "659",
    "country": "South Sudan",
    "code": "SS"
},
{
    "dmrid": "702",
    "country": "Belize",
    "code": "BZ"
},
{
    "dmrid": "704",
    "country": "Guatemala",
    "code": "GT"
},
{
    "dmrid": "706",
    "country": "El Salvador",
    "code": "SV"
},
{
    "dmrid": "708",
    "country": "Honduras",
    "code": "HN"
},
{
    "dmrid": "710",
    "country": "Nicaragua",
    "code": "NI"
},
{
    "dmrid": "712",
    "country": "Costa Rica",
    "code": "CR"
},
{
    "dmrid": "714",
    "country": "Panama",
    "code": "PA"
},
{
    "dmrid": "716",
    "country": "Peru",
    "code": "PE"
},
{
    "dmrid": "722",
    "country": "Argentina",
    "code": "AR"
},
{
    "dmrid": "724",
    "country": "Brazil",
    "code": "BR"
},
{
    "dmrid": "730",
    "country": "Chile",
    "code": "CL"
},
{
    "dmrid": "732",
    "country": "Colombia",
    "code": "CO"
},
{
    "dmrid": "734",
    "country": "Venezuela",
    "code": "VE"
},
{
    "dmrid": "736",
    "country": "Bolivia",
    "code": "BO"
},
{
    "dmrid": "738",
    "country": "Guyana",
    "code": "GY"
},
{
    "dmrid": "740",
    "country": "Ecuador",
    "code": "EC"
},
{
    "dmrid": "742",
    "country": "French Guiana",
    "code": "GF"
},
{
    "dmrid": "744",
    "country": "Paraguay",
    "code": "PY"
},
{
    "dmrid": "746",
    "country": "Suriname",
    "code": "SR"
},
{
    "dmrid": "748",
    "country": "Uruguay",
    "code": "UY"
},
{
    "dmrid": "750",
    "country": "Falkland Islands",
    "code": "FK"
}
];
