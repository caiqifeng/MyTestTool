<template>
  <div class="product-card">
    <h3>{{ product.name }}</h3>
    <p>Price: {{ product.price }}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Product } from '@shared/types';

export default defineComponent({
  name: 'ProductCard',
  props: {
    product: {
      type: Object as () => Product,
      required: true,
    },
  },
});
</script>