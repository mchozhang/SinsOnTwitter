new Chart(document.getElementById("barChart"), {
          type: 'bar',
          data: {
              // areas location
              labels: ["Africa", "Asia", "Europe", "Latin America", "North America"],

              datasets: [{
                  label: "Dataset 1",
                  backgroundColor: "#3e95cd",
                  data: [2478, 5267, 734, 784, 433],
                  boarderWidth: 1
              },
                  {
                      label: "Dataset 2",
                      backgroundColor: "#8e5ea2",
                      data: [2478, 5267, 734, 784, 433],
                      boarderWidth: 1
                  }
              ]
          },
          options: {
              maintainAspectRatio: false,
              responsive: true,
              legend: {display: false},
              title: {
                  display: true,
                  text: 'Predicted world population (millions) in 2050'
              }
          }
      });
