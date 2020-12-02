<template>
  <button v-bind="$attrs" v-on="$listeners" :class="{ Button: true, 'Button--big': 'big' in $attrs }"><slot /></button>
</template>

<style>
.Button {
  appearance: none;
  display: block;
  text-align: center;
  color: #fff;
  text-transform: uppercase;
  background: #096;
  padding: 6px 7px;
  font-family: 'Supria Sans W01 Bold', Arial, Helvetica, sans-serif;
  font-size: 12px;
  border: none;
  font-weight: bold;
}

.Button--big {
  padding: 10px 60px;
  font-size: 14px;
}
</style>
