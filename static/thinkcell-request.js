
var objPpttc = 
[
	{
		"template" : "https://static.think-cell.com/ppttc/template3.pptx",
		"data": [
			{
				"name": "Title",
				"table": [[{"string":"How many goals do the star players contribute?"}]]
			},
			{
				"name": "Left",
				"table": [[{"string":"Metropolis F.C. spends a lot of money and the star players reward this with a big contribution to the total goal count."}]]
			},
			{
				"name": "Center",
				"table": [[{"string":"Smallville's distribution of goals is much more equal. Beyond the three star players the rest of the team contributes a higher percentage of goals to the total."}]]
			},
			{
				"name": "Right",
				"table": [[{"string":"Upstart United has made a big splash with signing one big name only, and this shows in the goal counts."}]]
			},
			{
				"name": "LeftChartTitle",
				"table": [[{"string":"Goal counts for league leader: Metropolis F.C."}]]
			},
			{
				"name": "SourceLeft",
				"table": [[{"string":"Own fantasy (2019)"}]]
			},
			{
				"name": "RightChartTitle",
				"table": [[{"string":"Goal counts for top three clubs in league"}]]
			},
			{
				"name": "SourceRight",
				"table": [[{"string":"Some other report (2019)"}]]
			},
			{
				"name": "LeftChart",
				"table": [
					[null, {"string":"All other players"},{"string":"Messi"},{"string":"Ronaldo"},{"string":"Neymar"},{"string":"Total"}],
					[],
					[{"string":""},{"number":67},null,null,null,{"string":"e"}],
					[{"string":""},null,{"number":23},null,null,null],
					[{"string":""},null,null,{"number":17},null,null],
					[{"string":""},null,null,null,{"number":15},null]
				]
			},
			{
				"name": "RightChart",
				"table": [
					[null, {"string":"Metropolis F.C."},{"string":"Smallville Club"},{"string":"Upstart United"}],
					[],
					[{"string":"Star 1"},{"number":15},{"number":4},{"number":28}],
					[{"string":"Star 2"},{"number":17},{"number":6},{"number":6}],
					[{"string":"Star 3"},{"number":23},{"number":8},{"number":3}],
					[{"string":"All other players"},{"number":67},{"number":101},{"number":45}]
				]
			}
		]
	},
	{
		"template" : "https://static.think-cell.com/ppttc/template3.pptx",
		"data": [
			{
				"name": "Title",
				"table": [[{"string":"But how much do these wonder boys cost?"}]]
			},
			{
				"name": "Left",
				"table": [[{"string":"Metropolis F.C. has the money. Enough said."}]]
			},
			{
				"name": "Center",
				"table": [[{"string":"Smallville would struggle without their dedicated fans. That constrains how much the club can spend on big names without endangering their loyalty. This has been much discussed in the recent book by super-fan Addi McFootball, written with journalist Peter Smith."}]]
			},
			{
				"name": "Right",
				"table": [[{"string":"There are rumors about Upstart ..."}]]
			},
			{
				"name": "LeftChartTitle",
				"table": [[{"string":"Player salaries"}]]
			},
			{
				"name": "SourceLeft",
				"table": [[{"string":"Own fantasy (2019)"}]]
			},
			{
				"name": "RightChartTitle",
				"table": [[{"string":"Salaries for top three clubs in league"}]]
			},
			{
				"name": "SourceRight",
				"table": [[{"string":"Some other report (2019)"}]]
			},
			{
				"name": "LeftChart",
				"table": [
					[null, {"string":"All other players"},{"string":"Messi"},{"string":"Ronaldo"},{"string":"Neymar"},{"string":"Total"}],
					[],
					[{"string":""},{"number":45},null,null,null,{"string":"e"}],
					[{"string":""},null,{"number":8},null,null,null],
					[{"string":""},null,null,{"number":11},null,null],
					[{"string":""},null,null,null,{"number":14},null]
				]
			},
			{
				"name": "RightChart",
				"table": [
					[null, {"string":"Metropolis F.C."},{"string":"Smallville Club"},{"string":"Upstart United"}],
					[],
					[{"string":"Star 1"},{"number":14},{"number":2},{"number":22}],
					[{"string":"Star 2"},{"number":11},{"number":3},{"number":1}],
					[{"string":"Star 3"},{"number":8},{"number":3},{"number":1}],
					[{"string":"All other players"},{"number":45},{"number":32},{"number":44}]
				]
			}
		]
	}
]

					
function DownloadFile(filename, blob) {
	// Data URI are not supported with IE and Edge for arbitrary MIME types
	// https://msdn.microsoft.com/en-us/library/cc848897(v=vs.85).aspx
	if (window.navigator.msSaveOrOpenBlob) {
		window.navigator.msSaveOrOpenBlob(blob, filename);
	} else {
		var url = window.URL.createObjectURL(blob);
		var elemDownloader = document.getElementById("downloader");
		elemDownloader.setAttribute("href", url);
		elemDownloader.setAttribute("download", filename);
		elemDownloader.click();
		window.URL.revokeObjectURL(url);
	}
}

function SendPpttcToServer() {
	var elemError = document.getElementById("error");
	var elemMessage = document.getElementById("message");
	elemError.textContent = "";
	elemMessage.textContent = "Processing on the server ...";

	var xhr = new XMLHttpRequest();
	xhr.open("POST", document.location, /*async*/true);
	xhr.responseType = "blob";
	xhr.setRequestHeader("Content-Type", "application/vnd.think-cell.ppttc+json");
	xhr.onreadystatechange = function() {
		if(this.readyState === 4) {
			if (this.status === 200) {
				DownloadFile("sample.pptx", this.response);
				elemError.textContent = "";
				elemMessage.textContent = "Success.";
			} else if(this.response) {
				var fr = new FileReader();
				fr.onload = function(event) {
					elemError.appendChild(document.createTextNode(event.target.result));
					elemMessage.textContent = "";
				};
				fr.readAsText(this.response);
			} else {
				elemError.textContent = "";
				elemMessage.textContent = "Server connection failed.";
			}
		}
	};
	xhr.send(JSON.stringify(objPpttc));
}

