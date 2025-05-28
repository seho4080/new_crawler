<script setup>
  import { useDate } from "@/composables/useDate";
  import { defineProps, defineEmits } from "vue";

  const props = defineProps({
    data: {
      type: Object,
      required: true
    }
  });

  const emit = defineEmits(['delete']);

  const { formatDate } = useDate();

  const handleDeleteButton = () => {
    // 미구현
  }
</script>

<template>
  <article class="comment">    
    <div class="comment__header">
      <span class="comment__header-author">{{ props.data.username }}</span>
      <span class="comment__header-date">{{
        formatDate(props.data.created_at)
      }}</span>
      <button class="comment-delete-button" @click="handleDeleteButton">×</button>
    </div>
    <p class="comment__content">{{ props.data.content }}</p>
  </article>
</template>

<style scoped lang="scss">
.comment {
  padding: 10px;
  background-color: #f6f6f6;
  margin: 10px 0;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 7px;

  &__header {
    display: flex;
    gap: 10px;
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 5px;
    &-author {
      font-weight: bold;
    }
    &-date {
      color: #999;
      font-size: 0.8rem;
    }
  }
  &__content {
    font-size: 1rem;
    line-height: 1.4;
  }
}

.comment-delete-button {
  margin-left: auto;
  margin-right: 5px;
  color: red;
}
</style>
