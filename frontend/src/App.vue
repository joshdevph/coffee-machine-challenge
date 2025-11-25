<script setup>
import { computed, onMounted, ref } from 'vue'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

const drinks = [
  { key: 'espresso', label: 'Espresso', endpoint: '/coffee/espresso', usage: '8 g / 24 ml' },
  { key: 'double-espresso', label: 'Double Espresso', endpoint: '/coffee/double-espresso', usage: '16 g / 48 ml' },
  { key: 'ristretto', label: 'Ristretto', endpoint: '/coffee/ristretto', usage: '8 g / 16 ml' },
  { key: 'americano', label: 'Americano', endpoint: '/coffee/americano', usage: '16 g / 148 ml' }
]

const machineStatus = ref(null)
const waterAmount = ref(250)
const coffeeAmount = ref(50)
const loadingAction = ref('')
const errorMessage = ref('')
const events = ref([])

const isBusy = computed(() => Boolean(loadingAction.value))

const waterPercent = computed(() => {
  if (!machineStatus.value) return 0
  return Math.round((machineStatus.value.water.level / machineStatus.value.water.capacity) * 100)
})

const coffeePercent = computed(() => {
  if (!machineStatus.value) return 0
  return Math.round((machineStatus.value.coffee.level / machineStatus.value.coffee.capacity) * 100)
})

const lastMessage = computed(() => machineStatus.value?.last_message || 'No drinks brewed yet.')
const statusSummary = computed(() => describeStatus(machineStatus.value))

const MIN_WATER_REQUIRED = 148 // enough for an Americano, the most water-heavy recipe
const MIN_COFFEE_REQUIRED = 16 // enough for a double espresso/Americano, the most coffee-heavy recipe

function createId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function pushEvent(message, kind = 'info') {
  if (!message) return

  const entry = {
    id: createId(),
    message,
    kind,
    timestamp: new Date().toLocaleTimeString()
  }

  events.value = [entry, ...events.value].slice(0, 8)
}

async function callApi(path, options = {}) {
  errorMessage.value = ''
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      },
      ...options
    })

    let payload = {}
    try {
      payload = await response.json()
    } catch (parseError) {
      // ignore parsing issue and use empty payload
    }

    if (!response.ok) {
      const message = payload?.message || 'Request failed'
      throw new Error(message)
    }

    return payload
  } catch (networkError) {
    const message = networkError instanceof Error ? networkError.message : 'Unable to reach the API'
    throw new Error(message)
  }
}

function applyStatus(payload) {
  if (payload.status) {
    machineStatus.value = payload.status
  }
  if (payload.message) {
    pushEvent(payload.message)
  }
}

function describeStatus(status) {
  if (!status) return 'No status available.'
  const water = status.water
  const coffee = status.coffee

  if (water.level <= 0 && coffee.level <= 0) {
    return 'Both water and coffee are empty.'
  }
  if (water.level <= 0) {
    return 'Water container is empty.'
  }
  if (coffee.level <= 0) {
    return 'Coffee container is empty.'
  }
  const waterOk = water.level >= MIN_WATER_REQUIRED
  const coffeeOk = coffee.level >= MIN_COFFEE_REQUIRED

  if (!waterOk && !coffeeOk) {
    return `Low resources: water ${water.level}/${water.capacity} ml (< ${MIN_WATER_REQUIRED} ml), coffee ${coffee.level}/${coffee.capacity} g (< ${MIN_COFFEE_REQUIRED} g).`
  }
  if (!waterOk) {
    return `Low water: ${water.level}/${water.capacity} ml. At least ${MIN_WATER_REQUIRED} ml is needed for the largest drink.`
  }
  if (!coffeeOk) {
    return `Low coffee: ${coffee.level}/${coffee.capacity} g. At least ${MIN_COFFEE_REQUIRED} g is needed for the largest drink.`
  }
  if (water.level === water.capacity && coffee.level === coffee.capacity) {
    return 'Both containers are full and ready to brew.'
  }
  return `Ready to brew. Water: ${water.level}/${water.capacity} ml, Coffee: ${coffee.level}/${coffee.capacity} g.`
}

async function runAction(actionName, fn) {
  loadingAction.value = actionName
  try {
    await fn()
  } catch (error) {
    errorMessage.value = error.message
    pushEvent(error.message, 'error')
  } finally {
    loadingAction.value = ''
  }
}

async function brewDrink(drink) {
  await runAction(drink.key, async () => {
    const payload = await callApi(drink.endpoint, { method: 'POST' })
    applyStatus(payload)
  })
}

async function fetchStatus() {
  await runAction('status', async () => {
    const previousMessage = machineStatus.value?.last_message
    const payload = await callApi('/status')
    applyStatus(payload)
    const latestMessage = payload.status?.last_message
    if (latestMessage && latestMessage !== previousMessage) {
      pushEvent(latestMessage)
    }
    pushEvent(describeStatus(payload.status))
  })
}

async function fillWater() {
  if (waterAmount.value <= 0) {
    errorMessage.value = 'Water amount must be greater than 0.'
    return
  }

  await runAction('fill-water', async () => {
    const payload = await callApi('/containers/water/fill', {
      method: 'POST',
      body: JSON.stringify({ amount_ml: waterAmount.value })
    })
    applyStatus(payload)
  })
}

async function fillCoffee() {
  if (coffeeAmount.value <= 0) {
    errorMessage.value = 'Coffee amount must be greater than 0.'
    return
  }

  await runAction('fill-coffee', async () => {
    const payload = await callApi('/containers/coffee/fill', {
      method: 'POST',
      body: JSON.stringify({ amount_g: coffeeAmount.value })
    })
    applyStatus(payload)
  })
}

onMounted(() => {
  fetchStatus()
})
</script>

<template>
  <div class="app-shell">
    <header>
      <div>
        <p class="eyebrow">Coffee machine</p>
        <h1>Barista control panel</h1>
        <p class="lead">Brew drinks, keep resources topped up, and monitor the machine.</p>
      </div>
      <button class="secondary" :disabled="isBusy" @click="fetchStatus">
        {{ loadingAction === 'status' ? 'Refreshing...' : 'Check status' }}
      </button>
    </header>

    <div class="content-grid">
      <div class="main-column">
        <section aria-labelledby="brew-title">
          <div class="section-head">
            <div>
              <p class="eyebrow">Brew</p>
              <h2 id="brew-title">Make a drink</h2>
            </div>
          </div>
          <div class="card-grid">
            <button
              v-for="drink in drinks"
              :key="drink.key"
              class="action-card"
              :disabled="isBusy"
              @click="brewDrink(drink)"
            >
              <span class="action-title">{{ drink.label }}</span>
              <span class="action-subtitle">Uses {{ drink.usage }}</span>
            </button>
          </div>
        </section>

        <section class="fill" aria-labelledby="fill-title">
          <div>
            <p class="eyebrow">Refill</p>
            <h2 id="fill-title">Containers</h2>
          </div>
          <div class="fill-grid">
            <form @submit.prevent="fillWater">
              <label>Water amount (ml)</label>
              <input v-model.number="waterAmount" min="1" type="number" />
              <button :disabled="isBusy" type="submit">Fill water</button>
            </form>
            <form @submit.prevent="fillCoffee">
              <label>Coffee amount (g)</label>
              <input v-model.number="coffeeAmount" min="1" type="number" />
              <button :disabled="isBusy" type="submit">Fill coffee</button>
            </form>
          </div>
        </section>

        <section class="status" aria-labelledby="status-title">
          <div>
            <p class="eyebrow">Status</p>
            <h2 id="status-title">Resources</h2>
          </div>
          <p class="muted">{{ statusSummary }}</p>
          <div v-if="machineStatus" class="status-grid">
            <article>
              <h3>Water</h3>
              <p class="value">
                {{ machineStatus.water.level }} / {{ machineStatus.water.capacity }} {{ machineStatus.water.unit }}
              </p>
              <div class="progress">
                <span :style="{ width: `${waterPercent}%` }"></span>
              </div>
            </article>
            <article>
              <h3>Coffee</h3>
              <p class="value">
                {{ machineStatus.coffee.level }} / {{ machineStatus.coffee.capacity }} {{ machineStatus.coffee.unit }}
              </p>
              <div class="progress">
                <span :style="{ width: `${coffeePercent}%` }"></span>
              </div>
            </article>
          </div>
          <p v-else class="muted">Fetching machine state...</p>

          <div class="message-card">
            <h3>Latest message</h3>
            <p>{{ lastMessage }}</p>
          </div>
        </section>
      </div>

      <aside class="activity-column" aria-labelledby="event-title">
        <div>
          <p class="eyebrow">Activity</p>
          <h2 id="event-title">Recent events</h2>
        </div>
        <ul v-if="events.length" class="event-list">
          <li v-for="event in events" :key="event.id" :class="event.kind">
            <span class="time">{{ event.timestamp }}</span>
            <span>{{ event.message }}</span>
          </li>
        </ul>
        <p v-else class="muted">Nothing to report yet.</p>
      </aside>
    </div>

    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>
