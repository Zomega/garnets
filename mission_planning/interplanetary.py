# Basic KSP Interplanetary Transfer Calculator
# Based on http://ksp.olex.biz/

        data = {
                // all values in km and corresponding
                Kerbol: {
                        name: "Kerbol",
                        mu: 1167922000,
                        radius: 65400,
                        color: "yellow"
                },
                Moho: {
                        name: "Moho",
                        parent: "Kerbol",
                        alt: 5263138.3,
                        mu: 245.25,
                        radius: 250,
                        inclination: 7,
                        soi: 11206.449,
                        color: "brown"
                },
                Eve: {
                        name: "Eve",
                        parent: "Kerbol",
                        alt: 9832684.544,
                        mu: 8171.73,
                        radius: 700,
                        inclination: 2.1,
                        soi: 85109.364,
                        color: "purple"
                },
        Gilly: {
                        name: "Gilly",
                        parent: "Eve",
                        alt: 31500,
                        mu: 0.008289450,
                        radius: 13,
                        inclination: 12,
                        soi: 126.123,
                        color: "brown"
                },
                Kerbin: {
                        name: "Kerbin",
                        parent: "Kerbol",
                        alt: 13599840.256,
                        mu: 3531.6,
                        radius: 600,
                        inclination: 0,
                        soi: 84159.2865,
                        color: "skyblue"
                },
                Mun: {
                        name: "Mun",
                        parent: "Kerbin",
                        alt: 12000,
                        mu: 65.138,
                        radius: 200,
                        inclination: 0,
                        soi: 2430,
                        color: "gray"
                },
                Minmus: {
                        name: "Minmus",
                        parent: "Kerbin",
                        alt: 47000,
                        mu: 1.7658,
                        radius: 60,
                        inclination: 6,
                        soi: 2247.428,
                        color: "#97d0a9"
                },
                Duna: {
                        name: "Duna",
                        parent: "Kerbol",
                        alt: 20726155.264,
                        mu: 301.363,
                        radius: 320,
                        inclination: 1.85,
                        soi: 47921.949,
                        color: "orange"
                },
        Ike: {
                        name: "Ike",
                        parent: "Duna",
                        alt: 3200,
                        mu: 18.56837,
                        radius: 130,
                        inclination: 0.2,
                        soi: 1049.599,
                        color: "silver"
                },
                Dres: {
                        name: "Dres",
                        parent: "Kerbol",
                        alt: 40839348.203,
                        mu: 21.4845,
                        radius: 138,
                        inclination: 5,
                        soi: 32832.84,
                        color: "silver"
                },
                Jool: {
                        name: "Jool",
                        parent: "Kerbol",
                        alt: 68773560.320,
                        mu: 282528.0042,
                        radius: 6000,
                        inclination: 1.3,
                        soi: 2455985.185,
                        color: "green"
                },
        Laythe: {
                        name: "Laythe",
                        parent: "Jool",
                        alt: 27184,
                        mu: 1962,
                        radius: 500,
                        inclination: 0,
                        soi: 3723.646,
                        color: "darkblue"
                },
        Vall: {
                        name: "Vall",
                        parent: "Jool",
                        alt: 43152,
                        mu: 207.4815,
                        radius: 300,
                        inclination: 0,
                        soi: 2406.401,
                        color: "skyblue"
                },
        Tylo: {
                        name: "Tylo",
                        parent: "Jool",
                        alt: 68500,
                        mu: 2825.28,
                        radius: 600,
                        inclination: 0.025,
                        soi: 10856.51837,
                        color: "beige"
                },
        Bop: {
                        name: "Bop",
                        parent: "Jool",
                        alt: 104500,
                        mu: 2.486835,
                        radius: 65,
                        inclination: 15,
                        soi: 993.0028,
                        color: "brown"
                },
                Pol: {
                        name: "Pol",
                        parent: "Jool",
                        alt: 129890,
                        mu: 0.227,
                        radius: 44,
                        inclination: 1.304,
                        soi: 2455985.185,
                        color: "orange"
                },
				Eeloo: {
					name: "Eeloo",
					parent: "Kerbol",
					alt: 90118858.179,
					mu: 74.410815,
					radius: 210,
					inclination: 6.15,
					soi: 119082.94,
					color: "#ddd"
				}
				
        };
       
        function validateInputs() {
                $("#same-warning,#inclination-warning,#parent-warning,#speculation-warning").hide();
                $("#phase,#ejection,#velocity,#deltav").val("Not calculated");
                var o = $("#origin").find(":selected").text();
                var d = $("#destination").find(":selected").text();
                errorFree = true;
                if (o == d) {
                        errorFree = false;
                        $("#same-warning").show();
                }
                if (data[o].parent != data[d].parent) {
                        errorFree = false;
                        $("#parent-warning").show();
                }
               
                return errorFree;
        }
       
        function doTheMaths() {
                var o = data[$("#origin").find(":selected").text()];
                var d = data[$("#destination").find(":selected").text()];
                var p = data[o.parent];
               
                // phase angle:
                var t_h = Math.PI * Math.sqrt(Math.pow(o.alt+d.alt, 3)/(8*p.mu));
                var phase = (180 - Math.sqrt(p.mu/d.alt) * (t_h/d.alt) * (180/Math.PI)) % 360;
                $("#phase").val("" + Math.round(phase*100)/100 + "Â°");
               
                // velocity:
                var exitAlt = o.alt + o.soi; // approximation for exiting on the "outside"
                var v2 = Math.sqrt(p.mu/exitAlt) * (Math.sqrt((2*d.alt)/(exitAlt+d.alt)) - 1);
                var r = o.radius + parseInt($("#orbit").val());
                var v = Math.sqrt( (r* (o.soi*v2*v2 - 2*o.mu) + 2*o.soi*o.mu) / (r*o.soi) );
                $("#velocity").val("" + Math.round(v*100000)/100 + " m/s");
				
				// delta-v:
				var v_o = Math.sqrt(o.mu/r);
				var delta_v = v - v_o;
				$("#deltav").val("" + Math.round(delta_v*100000)/100 + " m/s");
               
                // ejection angle:
                var eta = v*v/2 - o.mu/r;
                var h = r * v;
                var e = Math.sqrt(1+((2*eta*h*h)/(o.mu*o.mu)));
                var eject = (180 - (Math.acos(1/e) * (180/Math.PI))) % 360;
               
                if (e < 1) {
                        // maltesh's solution for elliptical transfers
                        var a = -o.mu/(2*eta);
                        var l = a*(1-e*e);
                        var nu = Math.acos((l-o.soi)/(e*o.soi));
                        var phi = Math.atan2((e*Math.sin(nu)), (1+e*Math.cos(nu)));
                        //eject = (270 - (phi*180/Math.PI)) % 360;
                       
                        // Kosmo-nots fix to maltesh's solution
                        eject = (90 - (phi*180/Math.PI) + (nu*180/Math.PI)) % 360;
                }
               
                $("#ejection").val("" + Math.round(eject*100)/100 + "Â°");             
               
                // warning for different inclination
                if (o.inclination != d.inclination)
                        $("#inclination-warning").show();      
                       
                if (o.speculated || d.speculated)
                        $("#speculation-warning").show();      
 
                draw(o,d,p,Math.round(phase*100)/100,Math.round(eject*100)/100);
        }
       
        function draw(o,d,p,phase,eject) {
                // clear canvases
                $("#canvas-phase,#canvas-eject").clearCanvas();
               
                /*
                 * Planetary phase angle drawing
                 */
                var high = o.alt > d.alt ? o : d;
                var low = o.alt < d.alt ? o : d;
                               
                // higher orbit
                $("#canvas-phase").drawArc({
                        strokeStyle: "#aaa",
                        strokeWidth: 1,
                        x: 180, y: 180,
                        radius: 160
                });
               
                // lower orbit
                var lowerOrbit = Math.round(160*low.alt/high.alt);
                if (lowerOrbit < 30)
                        lowerOrbit = 30;
                $("#canvas-phase").drawArc({
                        strokeStyle: "#aaa",
                        strokeWidth: 1,
                        x: 180, y: 180,
                        radius: lowerOrbit
                });
               
                // origin body at 90Â° and its angle line
                var orbit = o == low ? lowerOrbit : 160;
                $("#canvas-phase").drawLine({
                        strokeStyle: "#f22",
                        strokeWidth: 1,
                        x1: 180, y1: 180,
                        x2: 360, y2: 180
                });
                $("#canvas-phase").drawArc({
                        strokeStyle: o.color,
                        strokeWidth: 1,
                        fillStyle: o.color,
                        x: 180+orbit, y: 180,
                        radius: 5
                });
                $("#canvas-phase").drawText({
                        fillStyle: "#333",
                        font: "8pt Consolas, Courier New, monospace",
                        text: o.name,
                        x: 180+orbit, y: 192
                });
               
                // destination body at 90Â° + phase angle and its line
                orbit = d == low ? lowerOrbit : 160;
                var rad = (-phase)*Math.PI/180; // phase > 0 = ccw, in radians
                var x = Math.round(180 + orbit * Math.cos(rad));
                var y = Math.round(180 + orbit * Math.sin(rad));
                var xl = Math.round(180 + 180 * Math.cos(rad));
                var yl = Math.round(180 + 180 * Math.sin(rad));
                $("#canvas-phase").drawLine({
                        strokeStyle: "#f22",
                        strokeWidth: 1,
                        x1: 180, y1: 180,
                        x2: xl, y2: yl
                });
                $("#canvas-phase").drawArc({
                        strokeStyle: d.color,
                        strokeWidth: 1,
                        fillStyle: d.color,
                        x: x, y: y,
                        radius: 5
                });
                $("#canvas-phase").drawText({
                        fillStyle: "#333",
                        font: "8pt Consolas, Courier New, monospace",
                        text: d.name,
                        x: x, y: y+12
                });
               
                // phase angle arc
                var arcRadius = (lowerOrbit <= 60) ? Math.round((160+lowerOrbit)/2) : Math.round(lowerOrbit/2);
                var arcStart = phase > 0 ? 90-phase : 90;
                var arcEnd = phase < 0 ? 90-phase : 90;
                $("#canvas-phase").drawArc({
                        strokeStyle: "#f22",
                        strokeWidth: 1,
                        x: 180, y: 180,
                        radius: arcRadius,
                        start: arcStart, end: arcEnd
                });
                var textX = Math.round(180 + (arcRadius+25) * Math.cos(rad/2));
                var textY = Math.round(180 + (arcRadius+25) * Math.sin(rad/2));
                $("#canvas-phase").drawText({
                        fillStyle: "#333",
                        font: "8pt Consolas, Courier New, monospace",
                        text: ""+phase+"Â°",
                        x: textX, y: textY
                });
               
                // parent
                $("#canvas-phase").drawArc({
                        strokeStyle: p.color,
                        strokeWidth: 1,
                        fillStyle: p.color,
                        x: 180, y: 180,
                        radius: 10
                });
                $("#canvas-phase").drawText({
                        fillStyle: "#333",
                        font: "8pt Consolas, Courier New, monospace",
                        text: p.name,
                        x: 180, y: 197
                });
               
                /*
                 * Ejection angle drawing
                 */
               
                // parking orbit
                $("#canvas-eject").drawArc({
                        strokeStyle: "#aaa",
                        strokeWidth: 1,
                        x: 180, y: 180,
                        radius: 60
                });
               
                // origin body's trajectory w/ prograde marker
                $("#canvas-eject").drawArc({
                        strokeStyle: o.color,
                        strokeWidth: 1,
                        x: -1820, y: 180,
                        radius: 2000
                });
               
                // spacecraft direction arrow
                var shipAngle = ((d.alt > o.alt) ? eject : eject - 180) % 360;
                $("#canvas-eject").drawArc({
                        strokeStyle: "#aaa",
                        strokeWidth: 1,
                        x: 180, y: 180,
                        radius: 80,
                        start: shipAngle-15, end: shipAngle+15
                });
                var arrowAngle = shipAngle - 15;
                var arrowRad = ((-90+arrowAngle)%360) * Math.PI / 180;
                var arrowX = 180 + 80*Math.cos(arrowRad);
                var arrowY = 180 + 80*Math.sin(arrowRad);
                $("#canvas-eject").drawPolygon({
                        fillStyle: "#aaa",
                        sides: 3,
                        radius: 6,
                        rotate: 270+arrowAngle,
                        x: arrowX, y: arrowY
                });    
               
                // pro/retrograde angle line and text
                $("#canvas-eject").drawLine({
                        strokeStyle: "#f22",
                        strokeWidth: 1,
                        x1: 180, y1: 180,
                        x2: 180, y2: (d.alt > o.alt) ? 0 : 360
                });
                $("#canvas-eject").drawText({
                        fillStyle: "#333",
                        font: "8pt Consolas, Courier New, monospace",
                        text: o.name + (d.alt > o.alt ? " prograde" : " retrograde"),
                        align: "left",
                        x: 185, y: (d.alt > o.alt) ? 10 : 350
                });
               
                // spacecraft and its angle line
                rad = (d.alt > o.alt) ?
                        (-90+eject%360)*Math.PI/180 : // ccw from prograde
                        ((90+eject)%360)*Math.PI/180; // cw from retrograde
                var x_s = Math.round(180 + 60 * Math.cos(rad));
                var y_s = Math.round(180 + 60 * Math.sin(rad));
                xl = Math.round(180 + 180 * Math.cos(rad));
                yl = Math.round(180 + 180 * Math.sin(rad));
                $("#canvas-eject").drawLine({
                        strokeStyle: "#f22",
                        strokeWidth: 1,
                        x1: 180, y1: 180,
                        x2: xl, y2: yl
                });
                $("#canvas-eject").drawPolygon({
                        fillStyle: "#888",
                        sides: 3,
                        radius: 8,
                        x: x_s, y: y_s
                });
                $("#canvas-eject").drawText({
                        fillStyle: "#333",
                        font: "8pt Consolas, Courier New, monospace",
                        text: "Ship",
                        x: x_s, y: y_s+12
                });
               
                // ejection angle arc and text
                arcRadius = 120;
                arcStart = (d.alt > o.alt) ?
                        0 :// prograde: 0
                        180; // retrograde: ship at 180 - eject
                arcEnd = (d.alt > o.alt) ? eject : eject - 180;
                $("#canvas-eject").drawArc({
                        strokeStyle: "#f22",
                        strokeWidth: 1,
                        x: 180, y: 180,
                        radius: arcRadius,
                        start: arcStart, end: arcEnd
                });
                var textRad = ((((arcStart%360)+(arcEnd%360))/2)-90)*Math.PI/180; // magic.
                textX = Math.round(180 + 145 * Math.cos(textRad) * ((d.alt > o.alt) ? 1 : -1));
                textY = Math.round(180 + 145 * Math.sin(textRad) * ((d.alt > o.alt) ? 1 : -1));
           
                $("#canvas-eject").drawText({
                        fillStyle: "#333",
                        font: "8pt Consolas, Courier New, monospace",
                        text: ""+eject+"Â°",
                        x: textX, y: textY
                });
               
                // origin body
                $("#canvas-eject").drawArc({
                        strokeStyle: o.color,
                        strokeWidth: 1,
                        fillStyle: o.color,
                        x: 180, y: 180,
                        radius: 40
                });
                $("#canvas-eject").drawText({
                        fillStyle: "#fff",
                        font: "8pt Consolas, Courier New, monospace",
                        text: o.name,
                        x: 180, y: 180
                });
               
               
        }
       
        $("#calculator").submit(function(event){
                if (validateInputs()) {
                        doTheMaths();
                }
                return false;
        });
       
        $("#reset").click(function(event){
                $("#same-warning,#inclination-warning,#parent-warning,#speculation-warning").hide();
                return true;
        });
       
        $("#origin,#destination,#orbit").change(function(event){
                validateInputs();
        });
       
        doTheMaths();
