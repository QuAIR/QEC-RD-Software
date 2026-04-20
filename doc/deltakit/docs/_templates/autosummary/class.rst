.. only:: html

   .. raw:: html

      <style>
      /* Hide the right "On this page" TOC in sphinxawesome-theme */
      nav.toc, .toc, .toc-sticky { display: none !important; }
      /* Optional: let the content use the freed space */
      main { grid-template-columns: minmax(0, 1fr); }
      </style>

{{ fullname }}
{{ "=" * fullname|length }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :show-inheritance:

Methods
-------

.. autosummary::
   :toctree: methods/
   :nosignatures:
{% for m in methods %}
{% if not m.startswith("_") %}
   {{ objname }}.{{ m }}
{% endif %}
{% endfor %}
