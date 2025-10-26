document.addEventListener("DOMContentLoaded", () => {
  // -------- Infinite Logo Scroll (only 1 clone) --------
  const logoTrack = document.querySelector(".logo-track");
  if (logoTrack && !logoTrack.dataset.cloned) {
    const copy = logoTrack.cloneNode(true);
    copy.dataset.cloned = "true";
    logoTrack.parentElement.appendChild(copy);
    logoTrack.dataset.cloned = "true"; // mark original
  }

  // -------- Intersection Observer for Scroll Animations --------
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
      }
    });
  }, { threshold: 0.2 });

  document.querySelectorAll(".logo-section, .placement-section").forEach(section => {
    observer.observe(section);
  });

  // -------- Modal Popup Function --------
  function showPlacementModal(year) {
    const data = placementDetails[year];
    const modal = document.createElement("div");
    modal.classList.add("placement-modal");
    modal.innerHTML = `
      <div class="placement-modal-content">
        <h2>Placement Year ${year}</h2>
        <p><strong>Total Students Placed:</strong> ${data.total}</p>
        <p><strong>Top Recruiters:</strong></p>
        <ul>${data.companies.map(c => `<li>${c}</li>`).join("")}</ul>
        <button class="close-btn">Close</button>
      </div>
    `;
    document.body.appendChild(modal);

    modal.querySelector(".close-btn").onclick = () => modal.remove();
    modal.addEventListener("click", (e) => {
      if (e.target === modal) modal.remove();
    });
  }
});
// ===== Sidebar Toggle =====
document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.getElementById("toggle-btn");
  const links = document.querySelectorAll(".sidebar-menu a");

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  // Active link highlight
  const currentLocation = window.location.href;
  links.forEach(link => {
    if (link.href === currentLocation) {
      link.classList.add("active");
    }
  });
});

document.addEventListener("DOMContentLoaded", () => {
  // ...YOUR EXISTING CODE...

  // -------- Image Slider Auto-Slide --------
  const slider = document.querySelector('.image-slider .slides');
  const images = document.querySelectorAll('.image-slider img.card-img');
  let currentIndex = 0;
  const totalImages = images.length;

  const displayTime = 15000;
  const transitionTime = 1000;

  function showSlide(index) {
    slider.style.transform = `translateX(-${index * 950}px)`;
  }

  function nextSlide() {
    currentIndex = (currentIndex + 1) % totalImages;
    showSlide(currentIndex);
  }

  showSlide(currentIndex);

  setInterval(() => {
    nextSlide();
  }, displayTime + transitionTime);
});
// ===== Placement Bar Graph =====
document.addEventListener("DOMContentLoaded", () => {
  // Ensure Chart.js is loaded
  if (typeof Chart === "undefined") {
    console.error("Chart.js not loaded");
    return;
  }

  const ctx = document.getElementById("placementChart");
  if (!ctx) return; // Exit if chart element isn't found

  const placementData = {
    labels: ["2020", "2021", "2022", "2023", "2024"],
    datasets: [{
      label: "Students Placed",
      data: [120, 150, 180, 210, 260],
      backgroundColor: [
        "rgba(52, 152, 219, 0.9)",  // bright blue
        "rgba(41, 128, 185, 0.9)",  // deep blue
        "rgba(127, 140, 141, 0.9)", // grey
        "rgba(174, 182, 191, 0.9)", // light grey
        "rgba(189, 195, 199, 0.9)"  // very light grey-blue
      ],
      borderColor: [
        "rgba(41, 128, 185, 1)",
        "rgba(31, 97, 141, 1)",
        "rgba(127, 140, 141, 1)",
        "rgba(174, 182, 191, 1)",
        "rgba(189, 195, 199, 1)"
      ],
      borderWidth: 1.5,
      borderRadius: 8,
      hoverBackgroundColor: "rgba(255, 255, 255, 0.9)",
      hoverBorderColor: "rgba(41, 128, 185, 1)"
    }]
  };

  const placementChart = new Chart(ctx, {
    type: "bar",
    data: placementData,
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          labels: { color: "#2c3e50", font: { size: 14, weight: "bold" } }
        },
        title: {
          display: false
        },
      },
      scales: {
        x: {
          ticks: { color: "#2c3e50", font: { size: 13 } },
          grid: { display: false }
        },
        y: {
          ticks: { color: "#2c3e50", font: { size: 13 } },
          grid: { color: "rgba(200,200,200,0.2)" },
          beginAtZero: true
        }
      },
      animation: {
        duration: 1500,
        easing: "easeOutQuart"
      }
    }
  });
});
