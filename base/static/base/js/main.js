document.addEventListener("DOMContentLoaded", function () {
  const body = document.body;
  const navbar = document.querySelector(".navbar");
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");

  const syncNavbar = function () {
    if (navbar) {
      navbar.classList.toggle("is-scrolled", window.scrollY > 8);
    }
  };

  syncNavbar();
  window.addEventListener("scroll", syncNavbar, { passive: true });

  if (toggle && links) {
    toggle.addEventListener("click", function () {
      const isOpen = links.classList.toggle("open");
      body.classList.toggle("nav-open", isOpen);
      toggle.setAttribute("aria-expanded", String(isOpen));
      toggle.innerHTML = isOpen
        ? '<i class="fa-solid fa-xmark" aria-hidden="true"></i>'
        : '<i class="fa-solid fa-bars" aria-hidden="true"></i>';
    });

    links.querySelectorAll("a, button").forEach(function (item) {
      item.addEventListener("click", function () {
        links.classList.remove("open");
        body.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.innerHTML = '<i class="fa-solid fa-bars" aria-hidden="true"></i>';
      });
    });
  }

  document.querySelectorAll(".alert").forEach(function (alert) {
    setTimeout(function () {
      alert.style.opacity = "0";
      alert.style.transform = "translateX(18px)";
      setTimeout(function () {
        alert.remove();
      }, 450);
    }, 5500);
  });

  const revealItems = document.querySelectorAll(".card, .stat-card, .admin-stat-card, .admin-status-chip, .section-heading");
  if ("IntersectionObserver" in window) {
    revealItems.forEach(function (item) {
      item.classList.add("fade-in");
    });

    const revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });

    revealItems.forEach(function (item) {
      revealObserver.observe(item);
    });
  }

  document.querySelectorAll("[data-table-search]").forEach(function (input) {
    const target = document.querySelector(input.dataset.tableSearch);
    if (!target) return;

    input.addEventListener("input", function () {
      const query = input.value.trim().toLowerCase();
      target.querySelectorAll("tbody tr").forEach(function (row) {
        row.hidden = query.length > 0 && !row.textContent.toLowerCase().includes(query);
      });
    });
  });

  document.querySelectorAll("table[data-sortable]").forEach(function (table) {
    table.querySelectorAll("th[data-sort]").forEach(function (header, columnIndex) {
      header.setAttribute("tabindex", "0");
      header.setAttribute("role", "button");

      const sortRows = function () {
        const tbody = table.querySelector("tbody");
        const rows = Array.from(tbody.querySelectorAll("tr")).filter(function (row) {
          return row.children.length > 1;
        });
        const direction = header.dataset.direction === "asc" ? "desc" : "asc";

        table.querySelectorAll("th[data-sort]").forEach(function (item) {
          delete item.dataset.direction;
        });
        header.dataset.direction = direction;

        rows.sort(function (a, b) {
          const first = a.children[columnIndex].textContent.trim().toLowerCase();
          const second = b.children[columnIndex].textContent.trim().toLowerCase();
          return direction === "asc"
            ? first.localeCompare(second, "fr", { numeric: true })
            : second.localeCompare(first, "fr", { numeric: true });
        });

        rows.forEach(function (row) {
          tbody.appendChild(row);
        });
      };

      header.addEventListener("click", sortRows);
      header.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          sortRows();
        }
      });
    });
  });
});
