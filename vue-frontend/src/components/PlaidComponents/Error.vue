<!-- src/components/Error.vue -->
<template>
  <div>
    <div class="errorTop"></div>
    <div class="errorContainer">
      <div class="code">
        {{ error.status_code ? error.status_code : 'error' }}
      </div>
      <div class="errorContents">
        <div class="errorItem">
          <span class="errorTitle">Error code: </span>
          <span class="errorData">
            <div class="errorCode">
              {{ error.error_code }}
              <div class="pinkBox"></div>
            </div>
          </span>
        </div>
        <div class="errorItem">
          <span class="errorTitle">Type: </span>
          <span class="errorData">{{ error.error_type }}</span>
        </div>
        <div class="errorItem">
          <span class="errorTitle">Message: </span>
          <span class="errorMessage">
            {{ error.display_message || error.error_message }}
          </span>
        </div>
      </div>
      <a
        :href="path"
        target="_blank"
        class="learnMore"
      >
        Learn more
      </a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Error',
  props: {
    error: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      path: '',
      errorPaths: {
        ITEM_ERROR: 'item',
        INSTITUTION_ERROR: 'institution',
        API_ERROR: 'api',
        ASSET_REPORT_ERROR: 'assets',
        BANK_TRANSFER_ERROR: 'bank-transfers',
        INVALID_INPUT: 'invalid-input',
        INVALID_REQUEST: 'invalid-request',
        INVALID_RESULT: 'invalid-result',
        OAUTH_ERROR: 'oauth',
        PAYMENT_ERROR: 'payment',
        RATE_LIMIT_EXCEEDED: 'rate-limit-exceeded',
        RECAPTCHA_ERROR: 'recaptcha',
        SANDBOX_ERROR: 'sandbox',
      },
    };
  },
  watch: {
    error: {
      immediate: true,
      handler(newError) {
        const errorType = newError.error_type;
        const errorPath = this.errorPaths[errorType] || 'unknown';
        this.path = `https://plaid.com/docs/errors/${errorPath}/#${newError.error_code?.toLowerCase()}`;
      },
    },
  },
};
</script>

<style scoped>
.errorTop {
  width: 90%;
  height: 1px;
  border-top: 1px solid #e0e0e0; /* Replacing $black200 */
}

.errorContainer {
  display: grid;
  grid-template-columns: 15% 57% 28%;
  width: 100%;
  margin: 0;
  font-size: 1.4rem;
}

.code {
  margin: 20px 0px 20px 30px; /* Replacing '2 * $unit' and '3 * $unit' with pixel values */
  font-family: monospace; /* Replacing $font-stack-monospace */
  font-size: 1.4rem;
}

.errorContents {
  margin: 30px 40px; /* Replacing '3 * $unit' and '4 * $unit' with pixel values */
}

.errorItem {
  display: grid;
  grid-template-columns: 2fr 5fr;
  margin-bottom: 10px; /* Replacing '$unit' with '10px' */
}

.errorTitle {
  font-weight: bold;
  line-height: normal;
}

.errorData {
  line-height: normal;
  font-family: monospace; /* Replacing $font-stack-monospace */
  letter-spacing: 0.25px;
}

.errorCode {
  display: inline-block;
  position: relative;
}

.pinkBox {
  position: absolute;
  top: 50%;
  height: 6px;
  width: 100%;
  background-color: #ffcccc; /* Replacing $red200 */
  z-index: -1;
}

.errorMessage {
  line-height: normal;
}

.learnMore {
  display: inline-block;
  margin: 20px;
  margin-left: 30px; /* Replacing '2 * $unit' and '3 * $unit' with pixel values */
  width: 70%;
  text-align: center;
  padding: 10px;
  background-color: #007bff; /* Button background color */
  color: #fff; /* Button text color */
  text-decoration: none;
  border-radius: 4px;
}

.learnMore:hover {
  background-color: #0056b3; /* Darker shade on hover */
}
</style>
