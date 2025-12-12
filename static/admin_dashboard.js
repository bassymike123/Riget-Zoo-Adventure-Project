// static/admin.js

document.addEventListener('DOMContentLoaded', () => {

  // highlight nav link by URL

  document.querySelectorAll('.admin-nav .nav-link').forEach(a=>{

    if (a.href === location.href || location.href.indexOf(a.getAttribute('href')) !== -1) {

      a.classList.add('active');

    }

    a.addEventListener('click', ()=> {

      document.querySelectorAll('.admin-nav .nav-link').forEach(x=>x.classList.remove('active'));

      a.classList.add('active');

    });

  });

  // small UX improvement: row click focusing (if present)

  document.querySelectorAll('.table tbody tr').forEach(row=>{

    row.addEventListener('mouseover', ()=> row.style.background = 'rgba(255,255,255,0.02)');

    row.addEventListener('mouseleave', ()=> row.style.background = 'transparent');

  });

});
 