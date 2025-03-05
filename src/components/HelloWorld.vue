<!-- @format -->

<script setup>
import { ref } from 'vue'

defineProps({
  msg: String,
})

const count = ref(0)
const content = ref('')
const currentUserId = ref('default_user')
const currentSessionId = ref('default_session')
const userSessions = ref({})

const testFunc = () => {
  const prompt = '第三高的呢？'
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
    <p>{{ content }}</p>
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
