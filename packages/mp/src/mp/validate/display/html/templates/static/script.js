/* Copyright 2025 Google LLC*/
/**/
/* Licensed under the Apache License, Version 2.0 (the "License");*/
/* you may not use this file except in compliance with the License.*/
/* You may obtain a copy of the License at*/
/**/
/*     http://www.apache.org/licenses/LICENSE-2.0*/
/**/
/* Unless required by applicable law or agreed to in writing, software*/
/* distributed under the License is distributed on an "AS IS" BASIS,*/
/* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.*/
/* See the License for the specific language governing permissions and*/
/* limitations under the License.*/

document.addEventListener('DOMContentLoaded', function() {
  /**
   * Toggles the visibility of collapsible content, typically used for accordions.
   * @param {HTMLElement} element The clicked element (e.g., accordion header) that triggers the toggle.
   */
  function toggleAccordion(element) {
    const content = element.nextElementSibling;
    if (content && content.classList.contains('collapsible-content')) {
      element.parentElement.classList.toggle('is-open');
      content.classList.toggle('is-open');
    }
  }

  /**
   * Switches between different tab contents based on the clicked tab button.
   * @param {HTMLElement} buttonElement The tab button that was clicked.
   * @param {string} categoryId The ID of the tab content div to display.
   */
  function switchTab(buttonElement, categoryId) {
    document.querySelectorAll('.tab-button').forEach(button => button.classList.remove('active'));
    buttonElement.classList.add('active');
    document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));
    const targetContent = document.getElementById('tab-content-' + categoryId);
    if (targetContent) {
      targetContent.classList.remove('hidden');
    }
  }

  /**
   * Downloads the current HTML page as an HTML file.
   */
  function downloadReport() {
    const htmlContent = document.documentElement.outerHTML;
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `validation-report-${new Date().toISOString().slice(0,10)}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }


  window.toggleAccordion = toggleAccordion;
  window.switchTab = switchTab;
  window.downloadReport = downloadReport;

  const firstTabButton = document.querySelector('.tab-button');
  if (firstTabButton) {
    firstTabButton.click();
  }
});