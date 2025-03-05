<!-- @format -->

<script setup>
import { ref } from 'vue'

defineProps({
  msg: String,
})

const count = ref(0)
const content = ref('')
const htmlContent = ref('')
const currentUserId = ref('default_user')
const currentSessionId = ref('default_session4')
const userSessions = ref({})

const testFunc = () => {
  const prompt = '世界上最高的山是哪座？'
  // const prompt = '5+7等于多少'

  fetch('/api/your-backend-endpoint', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: prompt,
      user_id: currentUserId.value,
      session_id: currentSessionId.value,
    }),
  })
    .then((response) => {
      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')

      function read() {
        return reader.read().then(({ done, value }) => {
          if (done) {
            console.log('Stream complete')
            return
          }
          console.log('value----:', value)

          const chunk = decoder.decode(value, { stream: true })
          console.log(chunk)
          content.value += chunk
          htmlContent.value = processResponse(content.value)
          return read()
        })
      }

      return read()
    })
    .catch((error) => console.error('Error:', error))
}

const fetchUserSessions = () => {
  const url = '/api/get-user-sessions'
  console.log('Fetching user sessions from:', url)
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: currentUserId.value,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return response.json()
    })
    .then((data) => {
      userSessions.value = data
      console.log('User sessions:', userSessions.value)
    })
    .catch((error) => console.error('Error fetching user sessions:', error))
}

function processResponse(response) {
  const lines = response.split('\n')
  let html = ''
  let inTable = false
  let tableRows = []
  let inCode = false
  let codeContent = ''

  lines.forEach((line) => {
    if (line.startsWith('### ')) {
      if (inTable) {
        html += buildTable(tableRows)
        tableRows = []
        inTable = false
      }
      if (inCode) {
        html += buildCode(codeContent)
        codeContent = ''
        inCode = false
      }
      html += `<h3>${line.replace('### ', '')}</h3>`
    } else if (line.startsWith('|')) {
      if (!inTable) {
        inTable = true
      }
      const cells = line.split('|').filter((cell) => cell.trim() !== '')
      tableRows.push(cells)
    } else if (line.startsWith('```')) {
      if (inCode) {
        html += buildCode(codeContent)
        codeContent = ''
        inCode = false
      } else {
        inCode = true
      }
    } else if (inCode) {
      codeContent += line + '\n'
    } else if (line.trim() !== '') {
      if (inTable) {
        html += buildTable(tableRows)
        tableRows = []
        inTable = false
      }
      html += `<p>${line}</p>`
    }
  })

  if (inTable) {
    html += buildTable(tableRows)
  }
  if (inCode) {
    html += buildCode(codeContent)
  }

  return html
}

function buildTable(rows) {
  let tableHTML = '<table>'
  rows.forEach((row, index) => {
    tableHTML += index === 0 ? '<thead><tr>' : '<tbody><tr>'
    row.forEach((cell) => {
      tableHTML += index === 0 ? `<th>${cell}</th>` : `<td>${cell}</td>`
    })
    tableHTML += index === 0 ? '</tr></thead>' : '</tr></tbody>'
  })
  tableHTML += '</table>'
  return tableHTML
}

function buildCode(code) {
  return `<pre><code class="language-javascript">${code.trim()}</code></pre>`
}

testFunc()
fetchUserSessions()
</script>

<template>
  <h1>{{ msg }}</h1>

  <div class="card">
    <button type="button" @click="count++">count is {{ count }}</button>
    <p>
      Edit
      <code>components/HelloWorld.vue</code> to test HMRy
    </p>
    <div v-html="htmlContent"></div>
  </div>

  <div>
    <h2>User Sessions</h2>
    <pre>{{ userSessions }}</pre>
  </div>

  <p>
    Check out
    <a href="https://vuejs.org/guide/quick-start.html#local" target="_blank">create-vue</a>, the official Vue + Vite
    starter
  </p>
  <p>
    Learn more about IDE Support for Vue in the
    <a href="https://vuejs.org/guide/scaling-up/tooling.html#ide-support" target="_blank">Vue Docs Scaling up Guide</a>.
  </p>
  <p class="read-the-docs">Click on the Vite and Vue logos to learn more</p>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
