cookieSettingsName = window.location.hostname+"_hbjson_settings";
settingsValidity = 5;	    // 5 days
settings = [ { config: { "theme": "theme-dark", hidetg: false, "last": 0 } }, { "map": { "zoom" : 6.5 } }, { name: "openbridges", "open": true }, {"name": "masters", "open": true }, { "name": "peers", "open": true }];

// localStorage.setItem('theme', themeName);
// localStorage.getItem('theme', themeName);

var zoomValue = 1;

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

function adjustMenuLayoutStyle(f) {
  siteHeader.style.transform = "scale(" + zoomValue + ")";
  siteHeader.style.marginTop = isFixed ?  "3.3rem":"0";
  menubar.style.position = isFixed ? "fixed":"relative";
  lockbutton.classList.remove(isFixed ? "fa-lock-open":"fa-lock")
  lockbutton.classList.add(isFixed ? "fa-lock":"fa-lock-open")
}

function initMenubar() {
    lockbutton = document.getElementById("lockButton");
    menubar = document.getElementById("menubar");
    siteHeader = document.getElementById("siteHeader");
    isFixed = true;

    lockbutton.addEventListener("click", () => {
        isFixed = !isFixed;
    
        adjustMenuLayoutStyle(isFixed);
    });
    
    adjustMenuLayoutStyle(isFixed);
}

String.prototype.capitalize = function (lower) {
    return (lower ? this.toLowerCase() : this).replace(/(?:^|\s|['`‘’.-])[^\x00-\x60^\x7B-\xDF](?!(\s|$))/g, function (a) {
        return a.toUpperCase();
    });
};

function zoom(v) {
	switch(v) {
		case -1: zoomValue -= 0.10; break;
		case  1: zoomValue += 0.10; break;
		default: zoomValue = 1;
	}

	document.getElementById("siteHeader").style["transform"] = "scale(" + zoomValue + ")";
	document.getElementById("siteHeader").style["transform-origin"] = "top center";
}

function enhanceNames(name) {
    if (name != null) {
        name = name.replace(/None/g, "");

        if (names != null && names[name] != null)
            return names[name].capitalize(true);
    }

    return name.capitalize(true);
}

function getTgTableState(name) {
    for(let i=0; i < settings.length; i++) {
        if (settings[i].name != null && settings[i].name == name)
            return settings[i];
    }

    return null;
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
    
    // document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + expires + "; path=/";
    document.cookie = name + "=" + value + expires + "; path=/";
}

function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
            return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function saveSettings() {
    themeSettings = document.documentElement.className;
    var ob = document.getElementById("openbridges").style.display != "none";
    var ma = document.getElementById("masters").style.display != "none";
    var pe = document.getElementById("peers").style.display != "none";

    settings = [
        { "config": { "theme": themeSettings, hidetg: hideAllTG, "last": Date.now() } },
        { "map": { "zoom" : (map != null) ? map.getZoom() : 6.5 } },
        { "name": "openbridges",    "open": ob, "colspan": $("#theadOpenbridges tr th").length }, 
        { "name": "masters",        "open": ma, "colspan": $("#theadMasters tr th").length }, 
        { "name": "peers",          "open": pe, "colspan": $("#theadPeers tr th").length }
    ];

    if (tgorder != null) {
        tgorder.forEach(tg => {
            var tgName = "tgId"+tg;
            var tgId = "hblink"+tg;
            if (document.getElementById(tgName) != null) {
                var visible = document.getElementById(tgId).style.display != "none";
                settings.push({ "name": tgId, "open": visible, "colspan": $("#" + tgName + " tr th").length });
            }
        });
    }
    
    createCookie(cookieSettingsName, JSON.stringify(settings), settingsValidity);

    // alert("Sauvegarde effectuée");
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

function applyConfig() {
    for(let i=0; i < settings.length; i++) {
        var tbs = settings[i];

        if (tbs.config) {
            themeSettings = tbs.config.theme;
            if (hideAllTG = tbs.config.hidetg)
			    $("#insertPoint").hide();
		    else
			    $("#insertPoint").show();
    
            if (themeSettings == "auto")
                adjustTheme();
            else
                document.documentElement.className = themeSettings;
        }
        else if (tbs.map)
            currentZoom = tbs.map.zoom;
        else if (tbs.open)
            $("#"+tbs.name).show();
        else
            $("#"+tbs.name).hide();
    }
}

function getConfigFromLocalStorage() {
    map = null;
    themeSettings = "theme-dark";

    // retrieve settings
    if ((cookie = JSON.parse(readCookie(cookieSettingsName))) == null) {
        cookie = settings;
        createCookie(cookieSettingsName, JSON.stringify(settings), settingsValidity);
    }
    else {
        if (cookie[0].config.last == null)
            cookie[0].config.last = 0;

        settings = cookie;
    }
}

const flag64 = [];
flag64["at"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUAgMAAADnxWVXAAAACVBMVEXtKTnzcHv///9FjJx3AAAAGklEQVQI12NgIAuEQkAAwyoIWEAaA66dLAAA/KEk6+/EHQQAAAAASUVORK5CYII=";
flag64["be"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABcAAAAUBAMAAACUkLs9AAAAElBMVEXtKTkAAAD64ELyZTtUTBZVTRYE41wOAAAAG0lEQVQY02MQFBQUVVJSUmYAASBHZMRw4N4GAFi9EENfoBrcAAAAAElFTkSuQmCC";
flag64["bo"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAUBAMAAACDsiv0AAAAD1BMVEXVKx4AeTT54wBTnSPhZhQzAYZEAAAAIUlEQVQY02NgoDFwQQEODEooQIHqfGMUYMAgiAIEqM0HACBCGM/oCyk+AAAAAElFTkSuQmCC";
flag64["ca"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAUCAMAAADImI+JAAAAM1BMVEX/AAD/MDD/EBD/19f/QED/ICD/r6//////wMD/8PD/oKD/YGD/gID/b2//cHD/UFD/kJAQFQNAAAAAgUlEQVQoz62S2woDIQxEj5doou7l/7+2DwXbwupa2nkIjBwyGAa68oW40vdgKUugmUi2BVAOOGQBjADxFtS8A+xZZ6DW5s8CUJpvVYegAcQ+bBzt3r0bR6fPhzTemPzL+jT7dejhLszPY/I0Yjd3NOJW6xaxhVKoLrbn/2AIvzT8AWsMCOs6h1CtAAAAAElFTkSuQmCC";
flag64["ch"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAANCAIAAAArLKlOAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFHSURBVChTlVIxTgQxDPTYyR7wlOv5PAW6hpIWCR7CQjaxGWf3CqSjYKSN4sQzHjuL11rl/8ALrEABfs6VWEQNQRiUGe4OU4bcmJkKug9cVE8wXmtosWTWYLqfW5u68nF3z3VXJOHLO0Md4byfhxFSKZlJkYQD3lm8975ubY0AzMLSXsQYEoIhnunph+EVlGndVbWaLSKFtgx41rRbFRpi8MctPdzE27KQ3F02hFIsIKxGmgbl/gR9fdMYgvaUw0K4ze5CjjHcBOvkfMlkh5dS2VKyRU7zCR5i43ruYybLOzsRWaXQIe3lEZxeObsM+HqO1Fuhn8LMA10LOSQ0ymcpH2O+I7VJJT0d8NXl1yTp25XTmn9AqOQcgScBq9tsr+r+7nu+mOWk1GMoNdNNeDrKU2fEOldT3PPiui8NvRf+AyXjSFFWdPcfPqrVgMZwDRUAAAAASUVORK5CYII=";
flag64["cl"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUBAMAAABohZD3AAAAFVBMVEUAOabVKx7///9Lc8AQRauQqNjf5vTwpxheAAAAKklEQVQY02NgAAElOGAgzDdG5bumhaDwWZQcUPjMxgakmY/KF0QFg40PAFkJGT1/YYOJAAAAAElFTkSuQmCC";
flag64["co"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUAgMAAADnxWVXAAAACVBMVEUAOJPOESb80RYoeTcGAAAAF0lEQVQI12NYBQELGKjOIAmEQkAAMQwA+9NB7HYGMdMAAAAASUVORK5CYII=";
flag64["de"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACEAAAAUBAMAAADxfUlCAAAAD1BMVEXdAAAAAAD/zgD0igBKAABdJSNsAAAAIUlEQVQY02MQRAMCDLQTcUEDDgz0BMZowIBBCQ0o0E4EAL4AHCF2rs9hAAAAAElFTkSuQmCC";
flag64["es"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUCAMAAACtdX32AAAAVFBMVEX/xACzTwzTsbr8wgDUiSvFawfvwy/GCx7uwBrdmDK/rDnztgDZkjPblALJcSSyZgexOhHNsCfNsCjHjmXnvjC9j068d1F4RUKYUB18TVWvSxy6kqEyHguVAAAAVklEQVQoz83RSRLAIAhEUVQgzpp5uv89cwKsuEr+9lU1C2BoBl/y26xtqSNyIoaQiJIx4nKtWov7mMtx64zS5Xjt5+aiwLyoohSzwJPHdUY/Qmf/fegDe6kKdhTlmsEAAAAASUVORK5CYII=";
flag64["fk"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAUCAMAAADImI+JAAAA8FBMVEUBIWlgdKHUeY4jdLnYVmvyxs1nbprIEC7AyNoOLHElQH0gPHv6+Pm/x9kTfMfg5O1icJ7f4+xklr////8CWmX88fP21dqlbVO3jnmytsDZ3OfOu7aDsdUfdbuBj5y6vb8cOXmwg24zTISwlooJKG6+zdja2tqftsiigXRroc+81epXgLAggcmanYH13uN2bYIxfL2PaGCRlqwwfL2hYD+VvNgwh8Wpvs5godBvUkWNn7tHV4ijj4tOaZtSlcSLm7Tu7u7O0tUAYY8faXCMrsfAmYNzg5Osp5mysX3JiGJooMevm2aorYO1gWPJw6hikagBkklFAAAA+0lEQVQoz8XQ126DMBSA4UOAGFOTKFA2guyddO+9m3S9/9vUJ8ZSLyJ82f8COJxPQhgMs6UBzyLEwnu9ZpiwLVwgFRCnpgZQQRFWMstxnGQZ+B4hLPBZwkdHbNo7m9olJFvaLOjRyXmDt09V0B0MR6OzU72EFi9hfsAI8fxgmeAsoO4O2T3LJATQWqZRq+PPaE18Kl9TvfFQxMWthILJ4/lDqf74tMuTUC7kgSMVMPPG6ffCyyhU15/M3z8Wn/NJXwFhNvh5e86LmcrBzfrl1Y3yK5Wz02v3a5XHoa2AcRrdTaeXneMDBTzs9HrjizCM9pTfpna3yy/w3/0CuwMWbh/ZsdkAAAAASUVORK5CYII=";
flag64["fr"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUAgMAAADnxWVXAAAACVBMVEUAI5XtKTn///+i/AH+AAAAFElEQVQI12NgYOBatSo0NIBh6DAATSAu4Xxi9HsAAAAASUVORK5CYII=";
flag64["frs"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAQCAMAAAAhxq8pAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAA8UExURf8AAP8HB/9aWv8GBv8ICP8hIf8YGP8yMv84OP9BQf9CQv8fH/8MDP9lZf8pKf8iIv9FRf8CAv8BAQAAAMJjVhgAAAAUdFJOU/////////////////////////8AT0/nEQAAAAlwSFlzAAAK8AAACvABQqw0mAAAAGFJREFUKFNtjkkSwCAIBMm+r/P/v4ZBSksjIg2NBwWVUEnfKIQZiJZd52seI6fe5BCl5ehdJqe/lHmpSKwKpf+gkHzGOcrQedWy7XGdpMjhXZLAaSjkZbhzqfcBXgo3RQAfnmEQfMJBNFUAAAAASUVORK5CYII=";
flag64["gb"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAUCAMAAADImI+JAAAAPFBMVEX////xw8p8jbLnv8pBWY8OLHHw8vfIEC4BIWnWTGKAkLRAWI5LYZXgeIn10tigrMfheYrx2+Htz9hKYJTy9LpmAAAAqUlEQVQoz8XTQRaDIAwFwC8SLBYE9f53LRVCCbJw1yx8koyiMcJOgFH04tBYUkDXBKnZLkldh4Z2kBnAJ2alO6SVqwrtgiSk9iaQ19EPktwL/RYuQ9c/Et45znB467dUyHAvq3AWgHtccJx+Ev+Ej19G53DBAFu0cc/wu/I2HsEVwA1PhSl1eK4NrxluuGTtJ5QUksmhaCkk68dM1SokGwxuoR0b/Qp5zw/L/xHkHUeiPgAAAABJRU5ErkJggg==";
flag64["it"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUAgMAAADnxWVXAAAACVBMVEUAkkbOKzf///85rJ3UAAAAFElEQVQI12NgYOBatSo0NIBh6DAATSAu4Xxi9HsAAAAASUVORK5CYII=";
flag64["jp"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUBAMAAABohZD3AAAAElBMVEW8AC3////NP2Dmn7DADzn77/GuzSpGAAAAP0lEQVQY02MQRAUM5PGNXJSR+UEMDAyqSHwFIJ8JwRdmAAFDOF8IzFeE80XAfEecfHT16Oah24fhHnT3ku9/AB+iE2XMgOg6AAAAAElFTkSuQmCC";
flag64["ma"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUBAMAAABohZD3AAAAFVBMVEXBJy1iQi5MSS+nLi2SNC2rLi15PC6Ld+IEAAAAKElEQVQY02NgGBjggsoNFjRF4TspqaDw2ZQSUPiMggIofGYGg4HxBwB4BQJD/6PdEAAAAABJRU5ErkJggg==";
flag64["mc"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAUAQMAAABCuQT+AAAABlBMVEXOESb///9W4q7JAAAAEklEQVQI12NgIBn8//+/gSQCAHAUIuOMnBoSAAAAAElFTkSuQmCC";
flag64["mu"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUAgMAAADnxWVXAAAADFBMVEUApVEaIG3qKDn/1QBAdqXLAAAAHUlEQVQI12NYBQELGIhhhEJAAFGM/xDwgSgGKQAAdktPG8262+oAAAAASUVORK5CYII=";
flag64["nl"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUBAMAAABohZD3AAAAD1BMVEUhRotrhLKuHCjIZm7///9fvUPgAAAAHElEQVQY02NUYkABTAzU5bMI4udT2z5GNPNpDQBo2wB0uX4S5QAAAABJRU5ErkJggg==";
flag64["pt"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUCAMAAACtdX32AAAAn1BMVEX/AADzVwDqkQBTkQAAYQD7PT2yweAAZgD4AADjfACQtADCzQD8LS3xaS/ujhzraA/ipQDsmwCbugDdvwCpvwD2WA/qjlLKmVKEqACjuQDT2ADNorbO1+vk4QBKhwDgoifYuADspFr5Vj6MkiCHnRw1fQDwblvtLwDXngDvfSPsQjPNrVu9nKr8Ryj6u7utiFv5czicrteesNe8n6H7u7sxBDfVAAAAhElEQVQoz2NgRwIMmIBe0iwceKSZuSQ1mBhxSTNr64uLqSkyYpcWkeLj4eXV1VTgxCotKcVqIsOmx6rOhE2ahVuCT4fN0JiPU5gDuzSrNJuRNCt2aXYuVS0DGTZeJUFBrHYLcSuL8vCIystidxq7nJCKuBi/AD/uYBERwB0shAKV/vENAM1rDK2atilmAAAAAElFTkSuQmCC";
flag64["re"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUAgMAAADnxWVXAAAACVBMVEUAI5XtKTn///+i/AH+AAAAFElEQVQI12NgYOBatSo0NIBh6DAATSAu4Xxi9HsAAAAASUVORK5CYII=";
flag64["ro"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUAgMAAADnxWVXAAAACVBMVEUAK3/OESb80RYeTc2tAAAAFElEQVQI12NgYOBatSo0NIBh6DAATSAu4Xxi9HsAAAAASUVORK5CYII=";
flag64["us"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAUCAMAAADWUb86AAAANlBMVEXGWWZ5eJtdQ25tbJI8O25IR3dUU4DZkZqyIjT///+VlbCFhKRgX4mrU2fY1+KaJj+5fpCqqcBFmxQnAAAAh0lEQVQoz8XPSwrDMAxFUau6T0ks9bf/zXYQKBTs4kGhZ6CR0LUbQhAEBOK+DzVchSpK4VI8tqEGqSiZwmXidgw1GaZIWajLaxql406PMnUxjRomEg91PGZRSMLo5+DaxmSk9CRLHfPZGhhR72tff0qS5wNn1y6fZmvHkvZbi9FtSduX/CX6Asb+ET4hHaT8AAAAAElFTkSuQmCC";
flag64["uy"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUCAMAAACtdX32AAAAVFBMVEX///+7iRX07ePOql0dTrGqvOL8+/o5ZLsAOKiOpti0ghru5dfCkyPTs3D69/Xo3MvGnUvZqgzhy5fQnwtPdcPiza7cwILizKPWuInhsBCbsd20xOU60XNuAAAAcklEQVQYGaXBWRLCIBBAwTdAJoRlsrl7/3vqP0qqtJtjqlmVb9x8qd4cnMYGYD6JLFkJsQHmi+ySNuUxNcDVtN5XqZmP9JrKXsrNeA4N0LMvSRZTQmwAzvm6zRnG0OBNLavxk9BF7GLo4sDURexi7OIvL5HoCsLqMEQ5AAAAAElFTkSuQmCC";
flag64["za"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUCAMAAACtdX32AAAAb1BMVEUAd0kJe0/sqRn8txv///9AT6fobWUAAAAAFIngPDH07vKneBFQOQiMwq0SDQLd7ecvg0CAlzE1k27UrSOqsdg+mHX1wL3qd29OXK0SJZHW6eLiSkA5hj7ariKPmy/0u7eHmTAzhD+Xx7TjTEKYyLXXNRCBAAAAj0lEQVQoz32RWRLCIBAFHwQliVGDxn1f7n9GgSzFIEP/dr0upgAA8Vb7T5UEnt26PqR1671YqsclpQuTC6CR2xcfgF4timcf2Jz/AtBaN/J2nQJzgtMucB8DiuB1EIjpdRBgtDS8tue1bNyWDf+0aWoP62YEkGl9LCkg01MZ6+BL4qnTmanTmemgxTc9tfwA2zUQndqOrtoAAAAASUVORK5CYII=";

flag64["noflag"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAANCAMAAACTkM4rAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAEXUExURQAAAJKSktXV1lNTUzs7O4mJibW1tVJSUtPT04iIiVVWVnd3eJqamr6+vuvr6/b29nJzc01NTygnJ8nHx+jo6PDw8Ovr7MrJyCMiIrGwsHx9fVFRUaioqJ2dnU9PT4aGhrOzsyMjIg4ODnd3dyoqKh8fH3h4eG5ubx0dHTMzM4B/fg8PDwQEBHRzc2xtbWlpaY6OjouLjGtra3V1dXd2djAwMKmop9LR0YyMjIyLi9PS0qOjozExMQUFBRkZGYeHiKCgoaKiooqLjH5+fmFhYp+goL2+vnBxcKOjore3tri4t2lqa7i5uZCQkWZmZhISEmlpare3uGpqapGRknx+fy0tLggICCMjJCQkJQkJCSwtLX+AgRsbGxD+1OUAAAAJcEhZcwAADr8AAA6/ATgFUyQAAACfSURBVBhXdcjXAoEAGEDhX5JVIdl7r+w9ighZZe/3fw4u/kvO3fngdwbCSJooykSaLVYkm51mWIeDZWin6z8B52Z5j4f3+jgEAH8gGApHorF4AgEgmUpnsrl8oVhCABDKlWqt3mi2BIRv7U631x8MR7gAojSeyAwjT2eSiKTMF0t1tVY327mCtCM0fX84HHWNOCFJ5wtcb/cHPF9vAPgAEyIU6qDlHbIAAAAASUVORK5CYII=";
flag64["shield"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAANCAMAAACTkM4rAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAABUUExURQAAAAUFBQoKCv///wEBAQ0NDQ8PDwMDAw4ODgICAhAQEC8vL6urqwYGBqqqqoGBgQQEBDExMQwMDBgYGM7OzgcHBxsbGxoaGggICB0dHT4+Pj09PdDhOekAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAB5SURBVBhXXY3bDoJADETH6aILaOUqIP//n7RdSYjz0uTMaQvc+BeAlEucpIo2zwirVFD090f29opyfSK3i1U3BYGt8Bno5a2dt48aGpvMt7IzlNiHFg/7wfaAbjRNJyc6umTa/FGXRHSZQzK2bl+Dum/rjzjyQxEAB6niBHSSJ9cvAAAAAElFTkSuQmCC";
flag64["unlicenced"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAANCAMAAACTkM4rAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAABUUExURQAAAAUFBQoKCv///wEBAQ0NDQ8PDwMDAw4ODgICAhAQEC8vL6urqwYGBqqqqoGBgQQEBDExMQwMDBgYGM7OzgcHBxsbGxoaGggICB0dHT4+Pj09PdDhOekAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAB5SURBVBhXXY3bDoJADETH6aILaOUqIP//n7RdSYjz0uTMaQvc+BeAlEucpIo2zwirVFD090f29opyfSK3i1U3BYGt8Bno5a2dt48aGpvMt7IzlNiHFg/7wfaAbjRNJyc6umTa/FGXRHSZQzK2bl+Dum/rjzjyQxEAB6niBHSSJ9cvAAAAAElFTkSuQmCC";

flag64["nabilla.png"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABcAAAAUCAYAAABmvqYOAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAMHSURBVEhLjZRdSFRBFMf/d7/XdNUVFV3NLUkhSM0EqUBNhKSntVCIJPYlkHooH3roLYrSCgmsh4pSI31I8yOIiAhBIegDXVoJwYrVcO0hKk1r3a97mzN79+Ou69oPzp7/nJk9c2buzAj4P1yis98qa46qrHWBOUUsHpXst6JQ9hCytnNjFPBAEpIlT7dX2yTmJVa1OhSKIrknKSadt7XRmDwejCNR8lVBgDTQeXq5p/UyUo16FlJBMBeGK45Qd2Avrp28gHOnmpcEQaBJVkM9IRR7rtWoJe/0Q66NVXZ4uhwYMYzh2JFaHovH7w9AM10M1dEiWgmP6az1FOd5YyuPJIZaC68vgBn3HA6x6jZDlCQ8e/9KboXwzY+To1VEk491t8uKLScjtIW9b58iMz2N60TodVr0jA+y5SsP3eiDK9xr+C9bTUVpUUhp9FBZaiDemgEsJuiLiuH7yqvZgKqgFsHhea4FS3RrKveUkNOFK/ddujPKhaH8OALdTiDfxNveoS+QPmXBs+5FSnEDN9ICKyCcmCCtLqzj+mJXLzlfZD12W41kq9+H/X9syM7NBTKMcg+bwO/D9Xcd2JZiYCUKMGekoSmnFekpyi3zB/y4MdWJz65F9A2+YCNlKHnf2GRkO+KhE+F685jlFmCtboE4Qhd0IzTO3tKoTM6gMn7z5PlMKrqAivZGOBdmuTYZU7E88JHreCg5g3KtxR5FugBnPH4vsKS4C5zXHSOyAmZvJ/7A4s+/5O4zWyMRW14bs35mK56bUyq9RgeY2b6LIrDMJmS4frgRCAawK0c+WXr2ApjYDf7lQdAXhPZsOUWp6hPM7lIjnmZmZmb8XSHbYcmW1qf6JHFmgFvgwyOpxJoX6ZeNzh/9N0Kit2WIGT//hw+WgT1acLm/o+elM/S+MLv33IG5+W+QFifQWFtFQ4kVZvTfCMqvpoReQy7iH6x4DDsb4PVGj3WYRJVzykuTJ4xl4km3rJRslnzYMXRVlltTXbmbnIM3YtgseZPsgUyLLJKjVqv4DFGAfzat/CEShbO6AAAAAElFTkSuQmCC";

function getTgFlag(id) {
    if (id.length > 2 && parseInt(id) > 100) {
        id = id.substring(0, 3);

        switch (id) {
            case "736":
            case "994":
                return flag64["unlicenced"]; // return "unlicenced.png"

            case "206":
                return flag64["be"]; // return "be.png";

            case "214":
                return flag64["es"]; // return "es.png";

            case "228":
                return flag64["ch"]; // return "ch.png";

            case "262":
            case "264":
                return flag64["de"]; // return "de.png";

            case "102":
            case "302":
                return flag64["ca"]; // return "ca.png";

            case "604":
                return flag64["ma"]; // return "ma.png";

            case "340":
            case "546":
            case "547":
            case "742":
            case "647":
            case "208":
                return flag64["fr"]; // return "fr.png";
/*
            // if you want to return several flags i.e (region / country)
            case 2623:
                return [ flag64["flag1"], flag64["flag2"]  ];
*/
            default:
                break;
        }

        for (let i = 0; i < mcc.length; i++) {
            if (mcc[i].dmrid == id) {
                var code = mcc[i].code.toLowerCase();

                if (flag64[code] != null)
                    return flag64[code];
                
                return "https://flagcdn.com/h20/" + code + ".png";
            }
        }
    }

    return flag64["shield"]; // "shield.png";
}

function getFlag(callsign, dmrid) {
    // console.log("'"+callsign + "' '" + dmrid+"'");

    if (dmrid.length > 2 && parseInt(dmrid) > 100) {
        // check if beacon has specific bitmap
        for (var key in tgbeacons) {
            if (dmrid == key) {
                if (flag64[tgbeacons[key]] != null)
                    return flag64[tgbeacons[key]];

                return tgbeacons[key];
            }
        }

        dmrid = dmrid.substring(0, 3);

        if (callsign.startsWith("FS"))
            return flag64["shield"]; // return "shield.png";

        if (callsign.startsWith("14FRS") || callsign.startsWith("FRS"))
            return flag64["frs"]; // return "frs.png";

        if (callsign.startsWith("BALISE") || dmrid.startsWith("14"))
            return flag64["unlicenced"]; // return "unlicenced.png";

        switch (dmrid) {
            case "736":
                if (dmrid.indexOf(callsign) != -1) 
                    break; // else fall through
            case "994":
                return flag64["unlicenced"]; // return "unlicenced.png";

            case "206":
                return flag64["be"]; // return "be.png";
            case "214":
                return flag64["es"]; // return "es.png";
            case "228":
                return flag64["ch"]; // 
            case "262":
            case "264":
                return flag64["de"]; // return "de.png";

            case "102":
            case "302":
                return flag64["ca"]; // return "ca.png";

            case "604":
                return flag64["ma"]; // return "ma.png";

            case "340":
            case "546":
            case "547":
            case "742":
            case "647":
            case "208":
                return flag64["fr"]; // return "fr.png";

            default:
                break;
        }

        for (let i = 0; i < mcc.length; i++) {
            if (mcc[i].dmrid == dmrid) {
                var code = mcc[i].code.toLowerCase();
                
                if (flag64[code] != null)
                    return flag64[code];

                return "https://flagcdn.com/h20/" + code + ".png";
            }
        }
    }

    return flag64["noflag"]; // noflag.png";
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

