<template functional>
  <button class="Delete" v-bind="props" v-on="listeners"><slot /> ❌</button>
</template>

<style>
.Delete{
  appearance: none;
  border: none;
  background: none;
  color: #666;
  font-size: 10px;
  font-family: 'Supria Sans W01 Regular', Arial, Helvetica, sans-serif;
  align-self: flex-end;
  cursor: pointer;
  margin: 0 0 5px;
  padding: 0;

  &:hover {
    text-decoration: underline;
  }
}
</style>
